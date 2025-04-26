importScripts("mark.min.js");

const filter = {
  url: [{ urlMatches: "https://*" }],
};

chrome.webNavigation.onCompleted.addListener((details) => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]?.id) {
      chrome.tabs.sendMessage(
        tabs[0].id,
        { action: "markPage", markList: ["hello", "world", "program"] },
        (response) => {
          console.log("Content script responded:", response);
        }
      );
    }
  });
}, filter);
