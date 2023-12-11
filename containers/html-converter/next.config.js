/** @type {import('next').NextConfig} */
const nextConfig = {}
const path = require('path')

module.exports = {
    sassOptions: {
        includePaths: [
            path.join(__dirname, "node_modules", "@uswds", "uswds", "packages"),
        ],
    },
}