module.exports = {
  devServer: {
    proxy: 'http://localhost:5000',
    watchOptions: {
      poll: 1000
    }
  }
}

