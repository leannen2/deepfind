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
        // console.log(results);
        currentIndex = 0;
        jumpTo();
      });
    },
  });
}

// Send HTML/PDF content and query to backend
async function getListOfSemanticMatches(contentType, query) {
  try {
    const html_content = document.documentElement.outerHTML;
    const res = await fetch('http://localhost:5002/api/find', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: html_content,
        contentType: contentType,
        query: query,
      }),
    });
    const response = await res.json();
    console.log("similar_terms", response.similar_terms)
    return response.similar_terms; 
  } catch (error) {
    console.error('Failed to get list of semantic matches:', error);
  }
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "markPage") {
    
    console.log("message received");
    
    getListOfSemanticMatches('html', message.query)
      .then((markList) => {
        if (markList && Array.isArray(markList)) {
          markAllTerms(markList);
        } else {
          console.warn("No terms received to mark.");
        }
      })
      .catch((err) => {
        console.error("Error getting semantic matches:", err);
      });
    sendResponse({ status: "ok" });
    return true;
  } else if (message.action === "jumpForward") {
    currentIndex = (currentIndex + 1) % results.length;
    jumpTo();
    sendResponse({ status: "ok" });
    return true;
  } else if (message.action === "jumpBackward") {
    currentIndex = (currentIndex - 1 + results.length) % results.length;
    jumpTo();
    sendResponse({ status: "ok" });
    return true;
  }
});



