const path = require("path");
const HTMLPlugin = require("html-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");
const HTMLPlugin = require("html-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  entry: {
    index: "./src/index.js",
    storage: "./src/storageIndex.js",
    index: "./src/index.js",
    storage: "./src/storageIndex.js",
  },
  mode: "production",
  mode: "production",
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: "babel-loader",
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
        },
        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
        exclude: /node_modules/,
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].css",
      filename: "[name].css",
    }),
    new CopyPlugin({
      patterns: [{ from: "manifest.json", to: "manifest.json" }],
    }),
    ...getHtmlPlugins(["index", "storage"]),
    ...getHtmlPlugins(["index", "storage"]),
  ],
  resolve: {
    extensions: [".js", ".jsx"],
    extensions: [".js", ".jsx"],
  },
  output: {
    path: path.join(__dirname, "dist"),
    filename: "js/[name].js", // JS still goes in dist/js
    path: path.join(__dirname, "dist"),
    filename: "js/[name].js", // JS still goes in dist/js
  },
};

function getHtmlPlugins(chunks) {
  return chunks.map(
    (chunk) =>
      new HTMLPlugin({
        template: `./public/${chunk}.html`, // <-- use custom HTML
        template: `./public/${chunk}.html`, // <-- use custom HTML
        filename: `${chunk}.html`,
        chunks: [chunk],
      })
  );
}
