/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
    sassOptions: {
        includePaths: [
            path.join(__dirname, "node_modules", "@uswds", "uswds", "packages"),
        ],
    },
    transpilePackages: ['yaml']
};

module.exports = nextConfig;