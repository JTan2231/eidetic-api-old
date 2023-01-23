const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')

module.exports = {
  entry: {
    api: './frontend/src/index.js',
    login: './frontend/src/pages/login/index.js',
    new_user: './frontend/src/pages/new_user/index.js',
    different_page: './frontend/src/pages/index/index.js',
  },
  output: {
    path: path.resolve('./api/static/api/'),
    filename: '[name]-[hash].js',
    publicPath: '',
  },
  plugins: [
    new CleanWebpackPlugin(),
    new BundleTracker({
      path: __dirname,
      filename: './webpack-stats.json',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
}

