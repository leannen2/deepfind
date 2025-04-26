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
    sendResponse({ status: "ok" });
    return true;
  }
});
