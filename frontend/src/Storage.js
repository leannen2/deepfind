import React, { useState, useEffect } from "react";

function Storage() {
  const [links, setLinks] = useState([]);
  const [activeGroup, setActiveGroup] = useState("default");
  const [groups, setGroups] = useState([]);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        chrome.identity.getAuthToken({ interactive: true }, async (token) => {
          if (chrome.runtime.lastError || !token) {
            console.error("Token error:", chrome.runtime.lastError);
            return;
          }

          const userInfoRes = await fetch("https://www.googleapis.com/oauth2/v1/userinfo", {
            headers: { Authorization: `Bearer ${token}` },
          });

          const userInfo = await userInfoRes.json();
          const userId = userInfo.id;
          if (!userId) return;

          const response = await fetch("http://127.0.0.1:5001/user/get_topics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ userId }),
          });

          const data = await response.json();
          setGroups(data.topics || []);
        });
      } catch (error) {
        console.error("Error fetching groups:", error);
      }
    };

    fetchGroups();
  }, []);

  const onClickGroup = async (group) => {
    setActiveGroup(group);

    try {
      chrome.identity.getAuthToken({ interactive: true }, async (token) => {
        if (chrome.runtime.lastError || !token) {
          console.error("Token error:", chrome.runtime.lastError);
          return;
        }

        const userInfoRes = await fetch("https://www.googleapis.com/oauth2/v1/userinfo", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const userInfo = await userInfoRes.json();
        const userId = userInfo.id;
        if (!userId) return;

        const response = await fetch("http://127.0.0.1:5001/user/get_links", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ userId, topic: group }),
        });

        const data = await response.json();
        setLinks(data.links || []);
      });
    } catch (error) {
      console.error("Error fetching links:", error);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r shadow-sm fixed md:relative z-10">
        <div className="p-6 border-b">
          <h1 className="text-xl font-semibold text-gray-800">Topics</h1>
        </div>
        <ul className="p-4 space-y-2">
          {groups.map((group) => (
            <li key={group}>
              <button
                onClick={() => onClickGroup(group)}
                className={`w-full text-left text-lg px-4 py-2 rounded-lg transition-colors duration-200 ${
                  activeGroup === group
                    ? "bg-blue-600 text-white"
                    : "hover:bg-blue-100 text-gray-800"
                }`}
              >
                {group}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main content */}
      <main className="flex-1 md:ml-64 p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Saved Links</h1>
          <p className="text-gray-500 text-lg">Group: <span className="font-medium">{activeGroup}</span></p>
        </div>

        {links.length === 0 ? (
          <p className="text-gray-500 italic">No links saved for this group.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {links.map((link, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow hover:shadow-lg transition-shadow duration-200"
              >
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-lg font-semibold text-blue-600 hover:underline"
                >
                  {link.title}
                </a>
                <p className="text-sm text-gray-500 mt-1">
                  Saved on:{" "}
                  {new Date(link.date_added).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Storage;
