"""AnimeGANv2 generator (face_paint_512_v2, bryandlee/animegan2-pytorch).
Architecture reverse-engineered from the .pt state-dict key structure and
verified by STRICT weight load (zero missing/unexpected keys). CPU-runnable.

Block grammar (from keys):
  ConvNormLReLU = Sequential(ReflectionPad(.0), Conv[bias=False](.1),
                             InstanceNorm(.2), LeakyReLU(0.2)(.3))
  InvertedResBlock(in,out,expand) as .layers = Sequential(
      ConvNormLReLU(in, in*expand, 1, 1),              # layers.0
      Sequential(ReflectionPad(1), DWConv[bias=True],  # layers.1
                 InstanceNorm),
      Conv2d(hidden, out, 1, bias=False),             # layers.2
      InstanceNorm)                                    # layers.3
    (+ residual when in == out)
  UpConvNormLReLU = Sequential(Upsample x2(.0), Conv(.1),
                               InstanceNorm(.2), LeakyReLU(.3))
"""
import torch
import torch.nn as nn


class ConvNormLReLU(nn.Sequential):
    def __init__(self, in_ch, out_ch, kernel_size=3, stride=1):
        super().__init__(
            nn.ReflectionPad2d(kernel_size // 2),
            nn.Conv2d(in_ch, out_ch, kernel_size, stride, padding=0, bias=False),
            nn.InstanceNorm2d(out_ch, affine=True),
            nn.LeakyReLU(0.2, inplace=True),
        )


class InvertedResBlock(nn.Module):
    def __init__(self, in_ch, out_ch, expand_ratio=2):
        super().__init__()
        hidden = in_ch * expand_ratio
        self.layers = nn.Sequential(
            ConvNormLReLU(in_ch, hidden, 1, 1),
            nn.Sequential(
                nn.ReflectionPad2d(1),
                nn.Conv2d(hidden, hidden, 3, 1, padding=0, groups=hidden, bias=True),
                nn.InstanceNorm2d(hidden, affine=True),
            ),
            nn.Conv2d(hidden, out_ch, 1, 1, 0, bias=False),
            nn.InstanceNorm2d(out_ch, affine=True),
        )
        self.use_res = (in_ch == out_ch)

    def forward(self, x):
        out = self.layers(x)
        return x + out if self.use_res else out


class UpConvNormLReLU(nn.Sequential):
    def __init__(self, in_ch, out_ch):
        super().__init__(
            nn.Upsample(scale_factor=2, mode="nearest"),
            nn.Conv2d(in_ch, out_ch, 3, 1, 1, bias=False),
            nn.InstanceNorm2d(out_ch, affine=True),
            nn.LeakyReLU(0.2, inplace=True),
        )


class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.block_a = nn.Sequential(
            ConvNormLReLU(3, 32, 7, 1),
            ConvNormLReLU(32, 64, 3, 2),
            ConvNormLReLU(64, 64, 3, 2),
        )
        self.block_b = nn.Sequential(
            ConvNormLReLU(64, 128, 3, 1),
            ConvNormLReLU(128, 128, 3, 2),
        )
        self.block_c = nn.Sequential(
            ConvNormLReLU(128, 128, 3, 1),
            InvertedResBlock(128, 256, 2),
            InvertedResBlock(256, 256, 2),
            InvertedResBlock(256, 256, 2),
            InvertedResBlock(256, 256, 2),
            ConvNormLReLU(256, 128, 3, 1),
        )
        self.block_d = nn.Sequential(
            UpConvNormLReLU(128, 128),
            UpConvNormLReLU(128, 128),
        )
        self.block_e = nn.Sequential(
            ConvNormLReLU(128, 64, 3, 1),
            ConvNormLReLU(64, 64, 3, 1),
            ConvNormLReLU(64, 32, 7, 1),
        )
        self.out_layer = nn.Sequential(
            nn.Conv2d(32, 3, 1, 1, 0, bias=False),
        )

    def forward(self, x):
        x = self.block_a(x)
        x = self.block_b(x)
        x = self.block_c(x)
        x = self.block_d(x)
        x = self.block_e(x)
        x = self.out_layer(x)
        return torch.tanh(x)
