const webpack = require('webpack');
const config = {
    entry: {
        index:  __dirname + '/js/index.jsx',
        control: __dirname + '/js/controlroom.jsx'
    },
    output: {
        path: __dirname + '/dist',
        filename: "[name].bundle.js",
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    module: {
        rules: [
            {
              test: /\.jsx?/,
              exclude: /node_modules/,
              use: 'babel-loader'
            }
          ]
    }
};
module.exports = config;
