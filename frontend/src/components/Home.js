"use client";

import React, { useState } from "react";

export default function Home() {
  const [search, setSearch] = useState("");
  const [includeImages, setIncludeImages] = useState(false);
  const [includeVideos, setIncludeVideos] = useState(false);

  return (
    <div className="w-[350px] border rounded-xl shadow-md p-4 bg-white">
      <div className="mb-4">
        <h2 className="text-lg font-bold">Ctrl++</h2>
        {/* <p className="text-sm text-gray-500">Ctrl+F and more.</p> */}
      </div>

      <div className="mb-4">
        <form>
          <div className="grid w-full gap-4">
            <div className="flex flex-col space-y-1.5">
              <label htmlFor="name" className="text-sm font-medium">
                Search
              </label>
              <input
                id="name"
                placeholder="..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </form>
      </div>

      <div className="flex justify-between items-start">
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="images"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="images" className="text-sm">
              Include images
            </label>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="videos"
              checked={includeVideos}
              onChange={(e) => setIncludeVideos(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="videos" className="text-sm">
              Include videos
            </label>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
          >
            {"<"}
          </button>
          <button
            type="button"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
          >
            {">"}
          </button>
        </div>
      </div>
    </div>
  );
}
