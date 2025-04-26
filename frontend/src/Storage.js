import React, { useState, useEffect } from "react";

function Storage() {
  const [activeGroup, setActiveGroup] = useState("default");
  const groups = ["backend", "api", "frontend"];

  const onClickGroup = (group) => {
    setActiveGroup(group);
  };
  return (
    <div className="flex">
      {/* Sidebar */}
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
