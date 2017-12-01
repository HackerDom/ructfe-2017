const HtmlWebpackPlugin = require("html-webpack-plugin");
const webpack = require("webpack");
const path = require("path");

module.exports = {
  entry: "./src/index.js",
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "../deploy/Static")
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: [
              [
                "@babel/preset-env",
                {
                  targets: {
                    browsers: ["last 2 Chrome versions"]
                  }
                }
              ],
              "@babel/preset-stage-2"
            ]
          }
        }
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: "Treasure map",
      template: "src/index.html"
    })
    // new webpack.optimize.UglifyJsPlugin({
    //   sourceMap: true,
    //   minimize: true,
    //   output: {
    //     comments: false
    //   },
    //   compress: {
    //     warnings: false,
    //     drop_debugger: true,
    //     dead_code: true,
    //     unused: true
    //   }
    // })
  ]
};
