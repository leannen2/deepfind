import React, { useState, useEffect } from "react";

function Storage() {
  const [links, setLinks] = useState([]);
  const [activeGroup, setActiveGroup] = useState("default");
  const [groups, setGroups] = useState([]);
  const [expandedLinks, setExpandedLinks] = useState({});

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
    setExpandedLinks({}); // Reset expanded state when changing groups

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

  const toggleExpand = (index) => {
    setExpandedLinks(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r shadow-sm fixed md:relative z-10 h-screen overflow-y-auto">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-xl font-semibold text-gray-800">Topics</h1>
        </div>
        <ul className="p-4 space-y-2">
          {groups.map((group) => (
            <li key={group}>
              <button
                onClick={() => onClickGroup(group)}
                className={`w-full text-left px-4 py-2.5 rounded-lg transition-all duration-200 ${
                  activeGroup === group
                    ? "bg-blue-600 text-white font-medium shadow-sm"
                    : "hover:bg-blue-50 text-gray-700"
                }`}
              >
                {group}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 md:ml-0">
        <div className="mb-8 border-b pb-4">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Saved Links</h1>
          <p className="text-gray-600">
            Group: <span className="font-medium text-blue-600">{activeGroup}</span>
          </p>
        </div>

        {links.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="bg-gray-100 rounded-full p-6 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-gray-500 text-lg">No links saved for this group yet.</p>
          </div>
        ) : (
          <div className="max-w-screen-lg mx-auto">
            <div className="grid grid-cols-1 gap-6">
              {links.map((link, index) => (
                <div
                  key={index}
                  className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 p-5"
                >
                  <div className="flex justify-between items-start mb-2">
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xl font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                    >
                      {link.title}
                    </a>
                    <button 
                      onClick={() => toggleExpand(index)}
                      className="text-gray-500 hover:text-gray-700 focus:outline-none p-1 rounded-full hover:bg-gray-100"
                      aria-expanded={expandedLinks[index]}
                      aria-label={expandedLinks[index] ? "Collapse text chunks" : "Expand text chunks"}
                    >
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        className={`h-5 w-5 transition-transform duration-200 ${expandedLinks[index] ? 'rotate-180' : ''}`} 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500 mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {new Date(link.date_added).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </div>
                  
                  {/* Collapsible text chunks section */}
                  <div 
                    className={`overflow-hidden transition-all duration-300 ${
                      expandedLinks[index] ? 'max-h-96 opacity-100 mt-3' : 'max-h-0 opacity-0'
                    }`}
                  >
                    <div className="border-t pt-3">
                      <h3 className="font-medium text-gray-700 mb-2">Text Chunks</h3>
                      <ul className="space-y-2">
                        {/* If link.chunks exists, map through them, otherwise show placeholder */}
                        {(link.textChunks || ['No text chunks available']).map((chunk, chunkIndex) => (
                          <li key={chunkIndex} className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700">
                            {chunk}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Storage;