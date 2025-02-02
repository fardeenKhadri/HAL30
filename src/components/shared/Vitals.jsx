import { useEffect, useState, useCallback, memo } from "react";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";

const toolObject = [
  {
    functionDeclarations: [
      {
        name: "look_at_lists",
        description:
          "Returns all current lists. Called immediately before calling `edit_list`, to ensure latest version is being edited.",
      },
      {
        name: "edit_list",
        description:
          "Edits list with specified id. Requires `id`, `heading`, and `list_array`. You must provide the complete new list array. May be called multiple times, once for each list requiring edit.",
        parameters: {
          type: "object",
          properties: {
            id: { type: "string" },
            heading: { type: "string" },
            list_array: {
              type: "array",
              items: { type: "string" },
            },
          },
          required: ["id", "heading", "list_array"],
        },
      },
      {
        name: "remove_list",
        description:
          "Removes the list with specified id. Requires `id`. May be called multiple times, once for each list you want to remove.",
        parameters: {
          type: "object",
          properties: { id: { type: "string" } },
          required: ["id"],
        },
      },
      {
        name: "create_list",
        description:
          "Creates new list. Requires `id`, `heading`, and `list_array`. May be called multiple times, once for each list you want to create.",
        parameters: {
          type: "object",
          properties: {
            id: { type: "string" },
            heading: { type: "string" },
            list_array: {
              type: "array",
              items: { type: "string" },
            },
          },
          required: ["id", "heading", "list_array"],
        },
      },
    ],
  },
];

const systemInstructionObject = {
  parts: [
    {
      text: `In this conversation, you will help the user create and manage checklists. Use tools to modify lists before responding.`,
    },
  ],
};

function Vitals() {
  const { client, setConfig, connect, connected } = useLiveAPIContext();

  useEffect(() => {
    setConfig({
      model: "models/gemini-2.0-flash-exp",
      generationConfig: {
        responseModalities: "audio",
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: "Aoede" } },
        },
      },
      systemInstruction: systemInstructionObject,
      tools: toolObject,
    });
  }, [setConfig]);

  const [isAwaitingFirstResponse, setIsAwaitingFirstResponse] = useState(false);
  const [initialMessage, setInitialMessage] = useState("");
  const [listsState, setListsState] = useState([]);
  const [toolResponse, setToolResponse] = useState(null);

  const updateList = useCallback((listId, updatedList) => {
    setListsState((prevLists) =>
      prevLists.map((list) =>
        list.id === listId ? { ...list, list_array: updatedList } : list
      )
    );
  }, []);

  const handleCheckboxChange = useCallback((listId, index) => {
    setListsState((prevLists) =>
      prevLists.map((list) => {
        if (list.id === listId) {
          const updatedList = [...list.list_array];
          const item = updatedList[index];
          updatedList[index] = item.startsWith("- [ ] ")
            ? item.replace("- [ ] ", "- [x] ")
            : item.replace("- [x] ", "- [ ] ");
          return { ...list, list_array: updatedList };
        }
        return list;
      })
    );
  }, []);

  const scrollToList = (id) => {
    setTimeout(() => {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 100);
  };

  useEffect(() => {
    const onToolCall = (toolCall) => {
      const functionResponses = [];
      toolCall.functionCalls.forEach((fCall) => {
        switch (fCall.name) {
          case "edit_list":
            updateList(fCall.args.id, fCall.args.list_array);
            break;
          case "remove_list":
            setListsState((prevLists) =>
              prevLists.filter((list) => list.id !== fCall.args.id)
            );
            break;
          case "create_list":
            const newList = {
              id: fCall.args.id,
              heading: fCall.args.heading,
              list_array: fCall.args.list_array,
              onListUpdate: updateList,
              onCheckboxChange: handleCheckboxChange,
            };
            setListsState((prevLists) => [...prevLists, newList]);
            scrollToList(newList.id);
            break;
        }
        functionResponses.push({
          id: fCall.id,
          name: fCall.name,
          response: { result: { string_value: `${fCall.name} OK.` } },
        });
      });
      setToolResponse({ functionResponses });
    };

    client.on("toolcall", onToolCall);
    return () => client.off("toolcall", onToolCall);
  }, [client, updateList, handleCheckboxChange]);

  useEffect(() => {
    if (toolResponse) {
      client.sendToolResponse({
        ...toolResponse,
        functionResponses: toolResponse.functionResponses.map((response) =>
          response.name === "look_at_lists"
            ? {
                ...response,
                response: { result: { object_value: listsState } },
              }
            : response
        ),
      });
      setToolResponse(null);
    }
  }, [toolResponse, listsState, client]);

  const connectAndSend = async (message) => {
    setIsAwaitingFirstResponse(true);
    if (!connected) await connect();
    client.send({ text: message });
  };

  const renderInitialScreen = () => (
    <div className="initial-screen">
      {!isAwaitingFirstResponse && (
        <>
          <div className="spacer"></div>
          <h1>📝 Start a list about:</h1>
          <input
            type="text"
            value={initialMessage}
            className="initialMessageInput"
            placeholder="type or say something..."
            onChange={(e) => setInitialMessage(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" &&
              connectAndSend(`Start a list about: ${initialMessage}`)
            }
          />
          <div className="spacer"></div>
          <div className="spacer"></div>
        </>
      )}
    </div>
  );

  const renderListScreen = () => (
    <div className="list-screen">hi{/* renders the list here */}</div>
  );

  return (
    <div className="app">
      {listsState.length === 0 ? renderInitialScreen() : renderListScreen()}
    </div>
  );
}

export const VitalsCheck = memo(Vitals);
