export default {
  server: {
    proxy: {
      "/login": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/me": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/usuarios": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/tatuagens": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
};
