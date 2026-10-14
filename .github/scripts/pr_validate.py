#!/usr/bin/env python3
"""Helpers for .github/workflows/pr-clean-merge.yml. Stdlib only.
  pr_validate.py json BASE HEAD   - parse every changed .json file
  pr_validate.py selftests        - run grid / promo-gate self-tests that exist in this repo
  pr_validate.py automerge        - wait for other checks, confirm mergeable, merge
"""
import json, os, subprocess, sys, time, glob

def run(cmd, **kw): print('+', ' '.join(cmd), flush=True); return subprocess.run(cmd, **kw)

def cmd_json(base, head):
    out = subprocess.run(['git', 'diff', '--no-renames', '--diff-filter=AM', '--name-only', f'{base}...{head}'],
                         capture_output=True, text=True, check=True).stdout.split()
    bad = 0; n = 0
    for p in out:
        if not p.endswith('.json') or not os.path.isfile(p) or '/node_modules/' in p: continue
        n += 1
        try: json.load(open(p, encoding='utf-8-sig'))
        except Exception as e: print(f'::error file={p}::invalid JSON: {e}'); bad += 1
    print(f'checked {n} changed JSON file(s), {bad} invalid'); sys.exit(1 if bad else 0)

def cmd_selftests():
    fails = 0; ran = 0
    for g in glob.glob('**/tools/grid.py', recursive=True):
        if 'node_modules' in g: continue
        tdir = os.path.join(os.path.dirname(os.path.dirname(g)), 'templates')
        for t in sorted(glob.glob(os.path.join(tdir, '*.json'))):
            ran += 1; r = run([sys.executable, g, t], capture_output=True, text=True)
            if r.returncode != 0: print(f'::error::{g} {t} exit {r.returncode}\n{r.stdout}{r.stderr}'); fails += 1
    for g in glob.glob('**/promo-pack-kit/scene_grid.py', recursive=True):
        ran += 1; r = run([sys.executable, g, '--template', 'el_toro'], capture_output=True, text=True)
        if r.returncode != 0: print(f'::error::{g} exit {r.returncode}\n{r.stderr}'); fails += 1
    for g in glob.glob('**/promo-pack-kit/promo_gates.py', recursive=True):
        # the bundled v1 metrics are KNOWN-BAD: the gates must fail them (exit 1). Exit 0 = gates prove nothing.
        ran += 1; r = run([sys.executable, g, '--self-test'], capture_output=True, text=True)
        if r.returncode != 1: print(f'::error::{g} --self-test should exit 1 on the v1 defects, got {r.returncode}\n{r.stdout[-2000:]}'); fails += 1
    print(f'self-tests run: {ran}, failed: {fails}'); sys.exit(1 if fails else 0)

def gh(*a): return subprocess.run(['gh', *a], capture_output=True, text=True)

def cmd_automerge():
    repo, pr, head, base, me = (os.environ[k] for k in ('REPO', 'PR', 'HEAD', 'BASE', 'SELF_RUN'))
    wf = subprocess.run(['git', 'diff', '--name-only', f'{base}...{head}', '--', '.github/workflows'], capture_output=True, text=True).stdout.strip()
    if wf: print('PR changes .github/workflows; GITHUB_TOKEN cannot merge it. Left open for the owner.'); return
    time.sleep(60)  # let every other workflow on this commit register its check runs first
    deadline = time.time() + 55 * 60
    while True:
        runs = json.loads(gh('api', f'repos/{repo}/commits/{head}/check-runs?per_page=100').stdout or '{}').get('check_runs', [])
        others = [c for c in runs if f'/runs/{me}/' not in (c.get('details_url') or '')]
        st = json.loads(gh('api', f'repos/{repo}/commits/{head}/status').stdout or '{}').get('statuses', [])
        pending = [c['name'] for c in others if c['status'] != 'completed'] + [s['context'] for s in st if s['state'] == 'pending']
        failed = [c['name'] for c in others if c['status'] == 'completed' and c['conclusion'] not in ('success', 'neutral', 'skipped')] \
               + [s['context'] for s in st if s['state'] in ('failure', 'error')]
        if failed: print('::error::other CI failed, not merging:', failed); sys.exit(1)
        if not pending: break
        if time.time() > deadline: print('::error::timed out waiting for', pending); sys.exit(1)
        print('waiting for', pending, flush=True); time.sleep(30)
    for _ in range(20):
        v = json.loads(gh('pr', 'view', pr, '-R', repo, '--json', 'mergeable,mergeStateStatus,headRefOid,state').stdout)
        if v['state'] != 'OPEN': print('PR is', v['state']); return
        if v['headRefOid'] != head: print('head moved; a newer run will handle it'); return
        if v['mergeable'] == 'MERGEABLE': break
        if v['mergeable'] == 'CONFLICTING': print('::error::PR has merge conflicts; stays open'); sys.exit(1)
        time.sleep(15)
    else: print('::error::mergeability unknown; stays open (UNKNOWN is never PASS)'); sys.exit(1)
    r = gh('pr', 'merge', pr, '-R', repo, '--auto', '--merge', '--match-head-commit', head)
    print(r.stdout, r.stderr)
    if r.returncode != 0:
        r = gh('pr', 'merge', pr, '-R', repo, '--merge', '--match-head-commit', head); print(r.stdout, r.stderr)
        sys.exit(r.returncode)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'json': cmd_json(sys.argv[2], sys.argv[3])
    elif c == 'selftests': cmd_selftests()
    elif c == 'automerge': cmd_automerge()
