const path = require('path');

module.exports = {
  devServer: {
    allowedHosts: 'all',
    host: '0.0.0.0',
    port: 3000,
    open: true,
    hot: true,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
};
