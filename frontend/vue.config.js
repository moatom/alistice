var HardSourceWebpackPlugin = require("hard-source-webpack-plugin");

module.exports = {
  assetsDir: "static",
  productionSourceMap: process.env.NODE_ENV === "development" ? true : false,
  configureWebpack: {
    plugins:
      process.env.NODE_ENV === "development" ? [new HardSourceWebpackPlugin()] : [],
    devtool: process.env.NODE_ENV === "development" ? "inline-source-map" : false
  }
};
