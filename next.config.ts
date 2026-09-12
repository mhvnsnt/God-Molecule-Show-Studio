import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The mock episode thumbnails are Unsplash URLs. Declared rather than
  // unoptimized so next/image stays available to anything added later.
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'images.unsplash.com' }],
  },
};

export default nextConfig;
