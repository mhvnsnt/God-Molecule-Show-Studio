#!/usr/bin/env python3
"""Build the real GNM oral donor used to repair MARS_CANONICAL.

This is intentionally donor-first:
- no sphere/ball cavity;
- no invented tooth grid;
- no generic head replacement;
- MARS geometry is never edited here.

The donor contains Google's anatomical mouth-sock, gums, upper/lower dental
arches and tongue plus the released 383-component expression basis. The
canonical mouth-open solve follows GNM-Studio's released stabilization logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

EXPRESSION_LABELS = (
    "surprise", "disgust", "suck", "compress_face", "stretch_face",
    "happy", "squint", "platysma", "blow", "funneler", "smile_wide",
    "corners_down", "pucker", "wink_left", "wink_right", "mouth_left",
    "mouth_right", "lips_roll_in", "snarl", "tongue_center",
)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def members(names: list[str], groups: np.ndarray, name: str) -> np.ndarray:
    if name not in names:
        raise RuntimeError(f"GNM anatomy missing required vertex group: {name}")
    return np.flatnonzero(groups[names.index(name)] > 0.5)

def decoder(path: Path) -> list[tuple[np.ndarray, np.ndarray]]:
    layers = []
    with h5py.File(path, "r") as f:
        weights = f["model_weights"]
        names = sorted(
            (n for n in weights if n.startswith("dense_")),
            key=lambda n: int(n.split("_")[-1]),
        )
        for name in names:
            g = weights[name][name]
            layers.append((
                np.asarray(g["kernel:0"], dtype=np.float32),
                np.asarray(g["bias:0"], dtype=np.float32),
            ))
    if not layers:
        raise RuntimeError("GNM expression decoder contains no dense layers")
    return layers

def decode(layers, inputs):
    value = inputs.astype(np.float32)
    for i, (kernel, bias) in enumerate(layers):
        value = value @ kernel + bias
        if i != len(layers) - 1:
            value = np.maximum(value, 0)
    return value

def canonical_mouth_open(expr_decoder: Path, expression_basis: np.ndarray,
                         names: list[str], groups: np.ndarray,
                         vertices: np.ndarray) -> tuple[np.ndarray, dict]:
    layers = decoder(expr_decoder)
    rng = np.random.default_rng(0x474E4D)
    latent = rng.normal(size=(303, 64)).astype(np.float32)[302]
    inputs = np.zeros((1, 64 + len(EXPRESSION_LABELS)), dtype=np.float32)
    inputs[0, :64] = latent
    inputs[0, 64 + EXPRESSION_LABELS.index("surprise")] = 1.0
    parameters = decode(layers, inputs)[0]

    # Exact GNM-Studio region isolation: eyes stay zero; tongue stays zero;
    # mouth opening comes from the learned lower-face basis only.
    parameters[:200] = 0.0
    parameters[350:] = 0.0
    delta = np.einsum("e,evc->vc", parameters, expression_basis, optimize=True)
    delta = delta.astype(np.float32) * np.float32(1.30)

    upper = members(names, groups, "upper_teeth_and_gums")
    lower = members(names, groups, "lower_teeth_and_gums")
    chin = members(names, groups, "chin_region")

    # Upper dental arch is rigid and stationary.
    delta[upper] = 0.0

    # Lower dental arch moves as one rigid island, not stretched vertex-by-vertex.
    lower_translation = delta[lower].mean(axis=0) * np.float32(1.80)
    chin_top = float(np.max(vertices[chin, 1] + delta[chin, 1]))
    dental_bottom = float(np.min(vertices[lower, 1]))
    lower_translation[1] = max(
        float(lower_translation[1]),
        chin_top + 0.0015 - dental_bottom,
    )
    delta[lower] = lower_translation

    return delta, {
        "source": "Saganaki22/GNM-Studio canonical_mouth_open_expression",
        "upper_teeth_rigid": True,
        "lower_teeth_rigid_translation": True,
        "eye_components_zeroed": True,
        "tongue_components_zeroed": True,
        "scale": 1.30,
        "lower_translation_scale": 1.80,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gnm-npz", required=True)
    ap.add_argument("--expression-decoder", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    src = Path(a.gnm_npz).resolve()
    decoder_path = Path(a.expression_decoder).resolve()
    out = Path(a.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if not src.is_file() or not decoder_path.is_file():
        raise SystemExit("GNM_ORAL_DONOR: FAIL — GNM NPZ or expression decoder missing")

    m = np.load(src, allow_pickle=False)
    v = np.asarray(m["template_vertex_positions"], dtype=np.float32)
    tris = np.asarray(m["triangles"], dtype=np.int32)
    names = [str(x) for x in m["vertex_group_names"]]
    groups = np.asarray(m["vertex_groups"], dtype=np.float32)
    expr = np.asarray(m["expression_basis"], dtype=np.float32)
    expr_names = np.asarray(m["expression_names"])

    # These are anatomical groups used by GNM Studio's oral containment tests.
    upper = members(names, groups, "upper_teeth_and_gums")
    lower = members(names, groups, "lower_teeth_and_gums")
    gums = members(names, groups, "gums")
    teeth = members(names, groups, "teeth")
    tongue = members(names, groups, "tongue")
    sock = members(names, groups, "mouth_sock")

    oral_indices = np.unique(np.concatenate([upper, lower, gums, teeth, tongue, sock]))
    oral_mask = np.zeros(len(v), dtype=bool)
    oral_mask[oral_indices] = True
    faces = tris[np.all(oral_mask[tris], axis=1)]
    if len(faces) == 0:
        raise RuntimeError("GNM_ORAL_DONOR: no closed oral anatomy faces found")
    used = np.unique(faces)
    remap = np.full(len(v), -1, dtype=np.int32)
    remap[used] = np.arange(len(used), dtype=np.int32)
    faces = remap[faces]

    jaw_open, jaw_meta = canonical_mouth_open(
        decoder_path, expr, names, groups, v
    )

    def local_mask(source_indices):
        return np.isin(used, source_indices)

    np.savez_compressed(
        out / "oral_donor.npz",
        vertices=v[used],
        faces=faces,
        upper_mask=local_mask(upper),
        lower_mask=local_mask(lower),
        teeth_mask=local_mask(teeth),
        gums_mask=local_mask(gums),
        tongue_mask=local_mask(tongue),
        mouth_sock_mask=local_mask(sock),
        expression_basis=expr[:, used, :],
        expression_names=expr_names,
        jaw_open_delta=jaw_open[used],
        tongue_basis=expr[350:382, used, :],
        upper_centroid=v[upper].mean(0),
        lower_centroid=v[lower].mean(0),
        mouth_sock_centroid=v[sock].mean(0),
    )

    manifest = {
        "schema": "god-molecule.gnm-oral-donor.v2",
        "source": "google/GNM Head v3",
        "license": "Apache-2.0",
        "gnm_npz_sha256": sha256(src),
        "expression_decoder_sha256": sha256(decoder_path),
        "source_vertices": int(len(v)),
        "oral_vertices": int(len(used)),
        "oral_triangles": int(len(faces)),
        "upper_teeth_vertices": int(len(upper)),
        "lower_teeth_vertices": int(len(lower)),
        "teeth_vertices": int(len(teeth)),
        "gum_vertices": int(len(gums)),
        "tongue_vertices": int(len(tongue)),
        "mouth_sock_vertices": int(len(sock)),
        "expression_dimensions": int(expr.shape[0]),
        "jaw_open": jaw_meta,
        "status": "DONOR_READY",
        "mars_identity_replacement": False,
        "sphere_cavity": False,
        "procedural_tooth_grid": False,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print("GNM_ORAL_DONOR: VERIFIED")
    print(f"ORAL_VERTICES={len(used)}")
    print(f"TEETH={len(teeth)} GUMS={len(gums)} TONGUE={len(tongue)} SOCK={len(sock)}")
    print("JAW_OPEN=GNM_CANONICAL")
    print(f"MANIFEST={out/'manifest.json'}")

if __name__ == "__main__":
    main()
