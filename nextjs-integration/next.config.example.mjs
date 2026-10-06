/** Merge this remote pattern into the EXISTING next.config instead of replacing it. */
const nextConfig={
  images:{
    remotePatterns:[
      {protocol:'https',hostname:'lon1.digitaloceanspaces.com'},
      {protocol:'https',hostname:'cms.ruffntumblekids.com'},
    ],
  },
};
export default nextConfig;
