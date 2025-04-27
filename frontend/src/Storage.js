import React, { useState, useEffect } from "react";

function Storage() {
  const [links, setLinks] = useState([]);
  const [activeGroup, setActiveGroup] = useState("default");
  const [groups, setGroups] = useState([]);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        // Step 1: Get OAuth token
        chrome.identity.getAuthToken({ interactive: true }, async (token) => {
          if (chrome.runtime.lastError || !token) {
            console.error("Token error:", chrome.runtime.lastError);
            return;
          }

          // Step 2: Get Google user info
          const userInfoRes = await fetch("https://www.googleapis.com/oauth2/v1/userinfo", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          const userInfo = await userInfoRes.json();
          const userId = userInfo.id;
          console.log("User ID:", userId);
          if (!userId) {
            console.error("User ID not found");
            return;
          }
          // Step 3: Fetch groups with userId in POST body
          const response = await fetch("http://127.0.0.1:5001/user/get_topics", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ userId }),
          });

          if (!response.ok) {
            throw new Error("Failed to fetch groups");
          }
          
          const data = await response.json();
          console.log("groups", data);
          setGroups(data.topics); // assuming data is an array of group names
        });
      } catch (error) {
        console.error("Error fetching groups:", error);
      }
    };

    fetchGroups();
  }, []);

  const onClickGroup = (group) => {
    setActiveGroup(group);
  };

  return (
    <div className="flex">
      {/* Sidebar */}}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-gray-800 text-white transform transition-transform duration-300 z-50 ${
          open ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0`}
      >
        <div className="p-4 text-lg font-bold border-b border-gray-700">
          Groups
        </div>
        <ul className="p-4 space-y-4">
          {groups.map((group) => (
            <li onClick={() => onClickGroup(group)}>
              <a href="#" className="text-md hover:text-gray-300">
                {group}
              </a>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex-1 md:ml-64">
        <div className="p-4 bg-gray-100 flex items-center justify-between md:hidden">
          <h1 className="text-xl font-semibold">My App</h1>
        </div>

        {/* Main content */}
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Welcome!</h2>
          <p>{activeGroup}</p>
        </div>
      </div>
    </div>
  );
}

export default Storage;
