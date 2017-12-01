const HtmlWebpackPlugin = require("html-webpack-plugin");
const webpack = require("webpack");
const path = require("path");
const isProd = process.env.NODE_ENV === "production";
let config = {
  entry: "./src/index.js",
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "../deploy/Static")
  },
  cache: true,
  module: {
    loaders: [
      {
        test: /\.js?$/,
        loader: "babel-loader",
        exclude: /node_modules/,
        include: [path.join(__dirname, "src")]
      },
      {
        test: /\.css$/,
        loaders: ["style-loader", "css-loader"]
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: "Treasure map",
      template: "src/index.html"
    }),
    new webpack.DefinePlugin({
      "process.env": {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV || "development")
      }
    })
  ]
};

if (isProd) {
  config.plugins.push(
    new webpack.NoErrorsPlugin(),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurrenceOrderPlugin(true),
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
      minimize: true,
      output: {
        comments: false
      },
      compress: {
        warnings: false,
        drop_debugger: true,
        dead_code: true,
        unused: true
      }
    })
  );
}

module.exports = config;
