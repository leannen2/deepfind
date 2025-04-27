importScripts("mark.min.js");

console.log("background.js")

const filter = {
  url: [{ urlMatches: "https://*" }],
};

async function loginWithGoogle() {
  return new Promise((resolve) => {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError) {
        console.error("Login error:", chrome.runtime.lastError.message);
        resolve(null);
      } else {
        console.log("Google OAuth token:", token);

        fetch("http://localhost:5001/auth/google", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("User info from backend:", data);
            resolve(data);
          })
          .catch((err) => {
            console.error("Backend error:", err);
            resolve(null);
          });
      }
    });
  });
}

// Call login on extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log("Extension started – attempting login");
  loginWithGoogle();
});

// Call login on extension install
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed – attempting login");
  loginWithGoogle();
});


// Run once when extension is installed or browser starts
chrome.runtime.onStartup.addListener(() => {
  console.log("Extension started – trying login");
  loginWithGoogle();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed – trying login");
  loginWithGoogle();
});

// chrome.webNavigation.onCompleted.addListener((details) => {
//   chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
//     if (tabs[0]?.id) {
//       chrome.tabs.sendMessage(
//         tabs[0].id,
//         { action: "markPage", markList: ["hello", "world", "program"] },
//         (response) => {
//           console.log("Content script responded:", response);
//         }
//       );
//     }
//   });
// }, filter);
