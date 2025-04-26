// content.js
console.log("Content script loaded");

const instance = new Mark(document.body);

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "markPage") {
    instance.unmark();
    message.markList.forEach((element) => {
      instance.mark(element);
    });
    // instance.mark("hello");
    // instance.mark("world");
    console.log("message received");
    
    fetch("http://127.0.0.1:5001/api/dummy")
    .then((res) => res.json())
    .then((data) => {
      console.log("API response from content.js:", data);
    })
    .catch((err) => {
      console.error("API error in content.js:", err);
    });
    sendResponse({ status: "ok" });
    return true;
  }
});
