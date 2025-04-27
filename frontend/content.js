// content.js
console.log("Content script loaded");

const instance = new Mark(document.body);

var results = [];
var markedImageElements = [];
var currentClass = "current";
// top offset for the jump (the search bar)
var offsetTop = 50;
// the current index of the focused element
var currentIndex = 0;

function jumpTo() {
  if (results.length > 0) {
    results.forEach((el) => (el.style.backgroundColor = "#E6E6FA"));

    const current = results[currentIndex];
    if (current) {
      current.style.backgroundColor = "#D8BFD8";
      const position =
        current.getBoundingClientRect().top + window.scrollY - offsetTop;
      window.scrollTo({ top: position, behavior: "smooth" });
    }
  }
}

function markTerm(term) {
  return new Promise((resolve) => {
    instance.mark(term, {
      separateWordSearch: false,
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

function markImages(imageSources) {
  var images = document.querySelectorAll("img");

  images.forEach((img) => {
    var imgSrc = img.getAttribute("src");
    if (imageSources.includes(imgSrc)) {
      markedImageElements.push(img);
      img.style.border = "3px solid #B57EDC";
      img.style.boxShadow = "0 0 10px 5px #E6E6FA";
      img.style.borderRadius = "5px";
    } else {
      img.style.border = "";
      img.style.boxShadow = "";
      img.style.borderRadius = "";
    }
  });

  console.log("markedImageElements", markedImageElements);
}

function unmarkAllImages() {
  var images = document.querySelectorAll("img");

  images.forEach((img) => {
    img.style.border = "";
    img.style.boxShadow = "";
    img.style.borderRadius = "";
  });
}

// Send HTML/PDF content and query to backend
async function getListOfSemanticMatches(contentType, query) {
  try {
    const html_content = document.documentElement.outerHTML;
    const res = await fetch("http://localhost:5001/api/find", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: html_content,
        contentType: contentType,
        query: query,
      }),
    });
    const response = await res.json();
    console.log("whole thing", response);
    return response;
  } catch (error) {
    console.error("Failed to get list of semantic matches:", error);
  }
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "markPage") {
    console.log("message received");
    results = [];
    getListOfSemanticMatches("html", message.query)
      .then((res) => {
        if (res.similar_terms && Array.isArray(res.similar_terms)) {
          markAllTerms(res.similar_terms);
        } else {
          console.warn("No terms received to mark.");
        }
        if (res.relevant_images && Array.isArray(res.relevant_images)) {
          markImages(res.relevant_images.map((relImage) => relImage.src));
        } else {
          console.log("no images highlighted");
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
