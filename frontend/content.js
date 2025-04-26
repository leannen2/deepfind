// content.js
console.log("Content script loaded");

const instance = new Mark(document.body);

var results = [];
var currentClass = "current";
// top offset for the jump (the search bar)
var offsetTop = 50;
// the current index of the focused element
var currentIndex = 0;

function jumpTo() {
  if (results.length > 0) {
    results.forEach((el) => (el.style.backgroundColor = "yellow"));

    const current = results[currentIndex];
    if (current) {
      current.style.backgroundColor = "orange";
      const position =
        current.getBoundingClientRect().top + window.scrollY - offsetTop;
      window.scrollTo({ top: position, behavior: "smooth" });
    }
  }
}

function markTerm(term) {
  return new Promise((resolve) => {
    instance.mark(term, {
      done: resolve,
    });
  });
}

function markAllTerms(terms) {
  instance.unmark({
    done: () => {
      Promise.all(terms.map((term) => markTerm(term))).then(() => {
        results = Array.from(document.body.querySelectorAll("mark"));
        console.log(results);
        currentIndex = 0;
        jumpTo();
      });
    },
  });
}


chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "markPage") {
    markAllTerms(message.markList);
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
  } else if (message.action === "jumpForward") {
    currentIndex++;
    jumpTo();
    sendResponse({ status: "ok" });
    return true;
  } else if (message.action === "jumpBackward") {
    currentIndex--;
    jumpTo();
    sendResponse({ status: "ok" });
    return true;
  }
});
