"use client";

import React, { useState, useEffect } from "react";

export default function Home() {
  const [search, setSearch] = useState("");
  const [topic, setTopic] = useState("Select topic");
  const [includeImages, setIncludeImages] = useState(false);
  const [includeVideos, setIncludeVideos] = useState(false);
  var userId = null;

  const [topics, setTopics] = useState([]);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5001/user/get_topics", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userId: userId,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to fetch topics");
        }

        const data = await response.json();
        console.log("topics: ", data);
        setTopics(data.topics);
      } catch (error) {
        console.error("Error fetching topics:", error);
      }
    };

    const getUserId = async () => {
      try {
        chrome.identity.getAuthToken({ interactive: true }, async (token) => {
          if (chrome.runtime.lastError || !token) {
            console.error("Token error:", chrome.runtime.lastError);
            return;
          }

          const userInfoRes = await fetch(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );

          const userInfo = await userInfoRes.json();
          userId = userInfo.id;
          fetchTopics();
          console.log("userId: ", userId);
        });
      } catch (error) {
        console.error("Error fetching groups:", error);
      }
    };

    getUserId();
    // fetchTopics();
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      if (
        typeof window !== "undefined" &&
        typeof window.chrome !== "undefined"
      ) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs[0]?.id) {
            chrome.tabs.sendMessage(
              tabs[0].id,
              { action: "markPage", query: search },
              (response) => console.log("Content script responded:", response)
            );
          }
        });
      }
    }
  };

  const handleJump = (direction) => {
    const action = direction === "forward" ? "jumpForward" : "jumpBackward";
    if (typeof window !== "undefined" && typeof window.chrome !== "undefined") {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]?.id) {
          chrome.tabs.sendMessage(tabs[0].id, { action }, (res) =>
            console.log("Jump response:", res)
          );
        }
      });
    }
  };

  const getCurrentTabUrl = () => {
    return new Promise((resolve) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        resolve(tabs[0]?.url || "");
      });
    });
  };

  const handleBookmark = async () => {
    try {
      chrome.identity.getAuthToken({ interactive: true }, async (token) => {
        if (chrome.runtime.lastError || !token) {
          console.error("Token error:", chrome.runtime.lastError);
          return;
        }

        try {
          const userInfoRes = await fetch(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );

          const userInfo = await userInfoRes.json();
          const userId = userInfo.id;
          if (!userId) return;

          const currentTabUrl = await getCurrentTabUrl();

          const response = await fetch("http://127.0.0.1:5001/user/add_link", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              userId,
              topic,
              link: {
                title: currentTabUrl,
                url: currentTabUrl,
              },
            }),
          });

          if (!response.ok) {
            throw new Error("Failed to add link");
          }

          const data = await response.json();
          console.log("add link data: ", data);
        } catch (error) {
          console.error("Error in async callback:", error);
        }
      });
    } catch (error) {
      console.error("Error calling getAuthToken:", error);
    }
  };

  const openStorage = () => {
    if (typeof window !== "undefined" && typeof window.chrome !== "undefined") {
      chrome.tabs.create({ url: chrome.runtime.getURL("storage.html") });
    }
  };

  const toggleDropdown = () => {
    const dropdown = document.getElementById("dropdown-menu");
    if (dropdown) {
      dropdown.classList.toggle("hidden");
    }
  };

  const selectTopic = (topic) => {
    setTopic(topic);
    const dropdown = document.getElementById("dropdown-menu");
    if (dropdown) {
      dropdown.classList.add("hidden");
    }
  };

  return (
    <div className="w-[350px] border rounded-2xl shadow-lg bg-white p-6 space-y-5 font-sans">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Ctrl++</h1>

        <div className="flex items-center gap-2">
          <div className="relative">
            <button
              onClick={toggleDropdown}
              className="text-sm bg-indigo-500 text-white px-3 py-1 rounded-md hover:bg-indigo-600 transition flex items-center"
            >
              {topic}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="ml-1"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
            <div
              id="dropdown-menu"
              className="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-md shadow-lg z-10 hidden"
            >
              {topics.map((topic) => (
                <button
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => selectTopic(topic)}
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleBookmark}
            className="p-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 transition"
            aria-label="Bookmark"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
              width="20"
              height="20"
              className="text-white"
            >
              <path d="M6 2C5.44772 2 5 2.44772 5 3V21.382C5 21.7655 5.42143 21.9875 5.72361 21.7764L12 17.118L18.2764 21.7764C18.5786 21.9875 19 21.7655 19 21.382V3C19 2.44772 18.5523 2 18 2H6Z" />
            </svg>
          </button>

          <button
            onClick={openStorage}
            className="p-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 transition"
            aria-label="Open Storage"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              width="20"
              height="20"
              className="text-white"
            >
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div>
        <input
          id="search"
          type="text"
          placeholder="Type something..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Options */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="images"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
              className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="images" className="text-sm text-gray-700">
              Include images
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="videos"
              checked={includeVideos}
              onChange={(e) => setIncludeVideos(e.target.checked)}
              className="w-4 h-4 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="videos" className="text-sm text-gray-700">
              Include videos
            </label>
          </div>
        </div>

        {/* Navigation Arrows */}
        <div className="flex gap-2">
          <button
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded-md text-lg transition"
            onClick={() => handleJump("backward")}
          >
            &lt;
          </button>
          <button
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded-md text-lg transition"
            onClick={() => handleJump("forward")}
          >
            &gt;
          </button>
        </div>
      </div>
    </div>
  );
}
