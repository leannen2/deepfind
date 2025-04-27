"use client";

import React, { useState } from "react";

export default function Home() {
  const [search, setSearch] = useState("");
  const [includeImages, setIncludeImages] = useState(false);
  const [includeVideos, setIncludeVideos] = useState(false);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
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
  };

  const handleJump = (direction) => {
    const action = direction === "forward" ? "jumpForward" : "jumpBackward";
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, { action }, (res) =>
          console.log("Jump response:", res)
        );
      }
    });
  };

  const openStorage = () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("storage.html") });
  };

  return (
    <div className="w-[350px] border rounded-2xl shadow-lg bg-white p-6 space-y-5 font-sans">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Ctrl++</h1>
        <button
          onClick={openStorage}
          className="text-sm bg-indigo-500 text-white px-3 py-1 rounded-md hover:bg-indigo-600 transition"
        >
          Open Storage
        </button>
      </div>

      {/* Search Input */}
      <div>
        {/* <label htmlFor="search" className="text-sm font-medium text-gray-700">
          Search
        </label> */}
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
