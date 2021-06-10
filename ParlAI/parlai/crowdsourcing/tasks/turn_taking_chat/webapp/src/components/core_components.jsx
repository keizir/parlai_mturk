/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useState } from "react";
import "bootstrap-chat/styles.css";
import { ChatApp, ChatMessage, DefaultTaskDescription } from "bootstrap-chat";

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  return (
    <div onClick={() => alert("You clicked on message with index " + idx)}>
      <ChatMessage
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        message={message.text}
        taskData={message.task_data}
        messageId={message.message_id}
      />
    </div>
  );
}

const Input = ({ handleAnswer }) => {
  const [submit, setSubmit] = useState(true);
  const [value, setValue] = useState("");
  
  const handleInput = (e) => {
    setValue(e.target.value);
    if (e.target.value.length > 0) {
      setSubmit(false);
    } else {
      setSubmit(true);
    }
  }

  return (
    <div className="field has-addons">
      <div className="control">
        <input className="input" type="text" placeholder="Input your answer" onChange={handleInput} />
      </div>
      <div className="control">
        <a className="button is-info" onClick={() => handleAnswer(value)} disabled={submit}>
          Send
        </a>
      </div>
    </div>
  )
}

function OnboardingComponent({ onSubmit }) {
  const [current, setCurrent] = useState(0);
  const [type, setType] = useState("");
  const [failed, setFailed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [disabled, setDisabled] = useState(false);
  // const inputEl = useRef(null);

  const questions = [
    {
      "bot": "In this practice exercise you will chat with a bot to assess your abilities. Sounds good?",
      "worker": [
        "Yes",
        "No"
      ],
      "answer": "Yes"
    },
    {
      "bot": "Okay. We're gonna talk about the movies. Do you like Movies?",
      "worker": [
        "Yes",
        "No"
      ],
      "answer": "Yes"
    },
    {
      "bot": "Great! What type of movies do you like?",
      "worker": [
        "Drama",
        "Action",
        "Horror",
        "Science Fiction",
        "History"
      ]
    },
    {
      "bot": "Awesome! Tell me why you like it?"
    },
    {
      "bot": "Congrats! You have successfully passed the test. Please click the below button to move forward. Thanks"
    }
  ];

  const handleNext = (cur, value) => {
    if (value === "No") {
      setFailed(true);
      onSubmit({ success: false });
      onSubmit({ success: false });
    } else {
      if (cur == 2) setType(value);
      // if (cur == 3) setAnswer(inputEl.current.value);
      setCurrent(current+1);
    }
  };

  const handleMove = () => {
    setDisabled(true);
    onSubmit({ success: true });
    onSubmit({ success: true });
  }

  const handleAnswer = (value) => {
    setAnswer(value);
    setCurrent(current+1);
  }

  const RenderChat = () => {
    const chats = [];
    for (let idx = 0; idx <= current; idx++) {
      chats.push(
        <>
          <div className="level-left block">
            <article className="message">
              <div className="message-body">
                {questions[idx]["bot"]}
              </div>
            </article>
          </div>
          <div className="level-right block">
            { idx < current
              ? <article className="message is-info">
                  <div className="message-body">
                    {idx < 2 && questions[idx]["answer"]}
                    {idx == 2 && type}
                    {idx == 3 && answer}
                  </div>
                </article>
              : <>
                  {idx < 3 && questions[idx]["worker"] && <div className="buttons">{questions[idx]["worker"].map((opt, key) => (
                      <button
                        key={key}
                        className="button is-link"
                        onClick={() => handleNext(idx, opt)}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>}
                  {idx == 3 &&
                    <Input handleAnswer={handleAnswer} />
                  }
                  {idx == 4 && <button
                      className="button is-link"
                      onClick={handleMove}
                      disabled={disabled}
                    >
                      Move to main task.
                    </button>
                  }
                </>
            }
          </div>
        </>
      );
    }

    return chats;
  }

  return (
    <div>
      <Directions>
        Instruction: This is a practice exercise similar to the main task. If you failed to answer, you are not able to move to main task.
      </Directions>
      <div className="container is-fullheight">
        <div className="box">
          { !failed
            ? <RenderChat />
            : <div className="level-left block">
                <article className="message is-warning">
                  <div className="message-body">
                    Sorry. You failed the test and you're not eligible to move forward. Please try to find another tasks.
                  </div>
                </article>
              </div>
          }
        </div>
      </div>
      
    </div>
  );
}

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function SimpleFrontend({ taskData, isOnboarding, onSubmit, onError }) {
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={onSubmit} />;
  }
  return (
    <ChatApp
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.message_id + "-" + idx}
        />
      )}
      renderSidePane={({ mephistoContext: { taskConfig } }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <p>This is a turn-taking chat with another person. Please see the instruction below:</p>
        </DefaultTaskDescription>
      )}
    />
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend };
