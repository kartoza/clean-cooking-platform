const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: {
    report_main: ['./static/eae/tool/report_main.js'],
    tool_main: ['./static/eae/tool/tool_main.js'],
  },
  output: {
    path: path.resolve('./static/webpack_bundles/'),
    filename: "[name]-[fullhash].js"
  },
  optimization: {
     splitChunks: {
       chunks: 'all',
     },
   },
  plugins: [
    new CleanWebpackPlugin(),
    new BundleTracker({filename: './webpack-stats.json'}),
  ],
}
