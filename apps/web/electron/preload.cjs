const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("stellaTower", {
  closeWindow: () => ipcRenderer.invoke("app:quit"),
});
