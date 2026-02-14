# Swift Sites Architecture

This document provides visual diagrams of the Swift Sites application architecture, focusing on the SSR rendering flow, LLM chat integration, and component selection system.

---

## Overall System Architecture

```mermaid
flowchart TB
    subgraph Browser["Browser (Client)"]
        subgraph MainWindow["Main Window"]
            Editor["YAML Editor<br/>(CodeMirror)"]
            PropsPanel["Properties Panel"]
            CompTree["Component Tree"]
            ChatUI["Chat UI<br/>(chat.js)"]
            ChatBubble["💬 Chat Bubble"]

            subgraph StateManagers["State Managers"]
                SelectionMgr["SelectionManager"]
                HistoryMgr["HistoryManager"]
                PathMap["PathMapBuilder"]
            end
        end

        subgraph IFrame["Preview Iframe"]
            PreviewBridge["preview_bridge.js"]
            RenderedHTML["Rendered Components"]
        end
    end

    subgraph FlaskServer["Flask Server (Python)"]
        AppPy["app.py<br/>App Factory"]
        ConfigPy["config.py"]
        ExtPy["extensions.py<br/>TOKENS, DEFAULTS"]
        Renderer["renderer.py"]
        LLMService["llm_service.py"]

        subgraph Blueprints["routes/ (Blueprints)"]
            ViewsBP["views.py"]
            RenderBP["render.py"]
            MetadataBP["metadata.py"]
            ImagesBP["images.py"]
            ChatBP["chat.py"]
        end

        subgraph Templates["Jinja2 Templates"]
            IndexHTML["index.html"]
            PreviewFrame["preview_frame.html"]
            ComponentMacros["components/<br/>28 macro files"]
        end

        subgraph StaticFiles["config/"]
            DefaultsYAML["component_defaults.yaml"]
            SchemasYAML["component_schemas.yaml"]
            SchemaTokensYAML["schema_tokens.yaml"]
        end

        TokensYAML["tokens.yaml"]
        LogFile["logs/llm_chat.log"]
    end

    subgraph External["External Services"]
        OllamaAPI["Ollama API<br/>(Cloud/Local)"]
        LLMGuide["LLM_COMPONENT_GUIDE.md"]
    end

    %% User Interactions
    User((User)) -->|"Types YAML"| Editor
    User -->|"Clicks component"| RenderedHTML
    User -->|"Opens chat"| ChatBubble
    User -->|"Sends message"| ChatUI

    %% App Wiring
    AppPy --> ConfigPy
    AppPy --> ExtPy
    AppPy --> Blueprints

    %% Editor Flow
    Editor -->|"POST /render"| RenderBP
    RenderBP --> Renderer
    Renderer --> ComponentMacros
    ComponentMacros -->|"HTML"| RenderBP
    RenderBP -->|"HTML Response"| Editor
    Editor -->|"postMessage<br/>UPDATE_CONTENT"| PreviewBridge
    PreviewBridge -->|"innerHTML"| RenderedHTML

    %% Selection Flow
    RenderedHTML -->|"Click"| PreviewBridge
    PreviewBridge -->|"postMessage<br/>COMPONENT_CLICKED"| SelectionMgr
    SelectionMgr -->|"CustomEvent<br/>swift-selection-changed"| ChatUI
    SelectionMgr -->|"Callback"| PropsPanel
    SelectionMgr -->|"postMessage<br/>SET_SELECTION"| PreviewBridge

    %% Chat Flow
    ChatUI -->|"POST /api/chat"| ChatBP
    ChatBP --> LLMService
    LLMService -->|"Load context"| LLMGuide
    LLMService -->|"API Request"| OllamaAPI
    OllamaAPI -->|"YAML Response"| LLMService
    LLMService -->|"Log"| LogFile
    LLMService -->|"Parsed Result"| ChatBP
    ChatBP -->|"JSON Response"| ChatUI
    ChatUI -->|"Apply YAML"| Editor

    %% Properties Panel Flow
    PropsPanel -->|"GET /api/schemas"| MetadataBP
    PropsPanel -->|"Update YAML"| Editor

    %% Styling
    classDef flask fill:#3572A5,color:white
    classDef js fill:#F7DF1E,color:black
    classDef external fill:#10B981,color:white
    classDef storage fill:#6B7280,color:white

    class AppPy,ConfigPy,ExtPy,Renderer,LLMService,ViewsBP,RenderBP,MetadataBP,ImagesBP,ChatBP flask
    class ChatUI,SelectionMgr,PreviewBridge,Editor js
    class OllamaAPI external
    class LogFile,TokensYAML,DefaultsYAML storage
```

---

## LLM Chat Flow (Sequence Diagram)

```mermaid
sequenceDiagram
    participant User
    participant ChatUI as Chat UI<br/>(chat.js)
    participant ChatService as chatService.js
    participant Flask as Flask /api/chat
    participant LLM as llm_service.py
    participant Ollama as Ollama API
    participant Log as llm_chat.log

    User->>ChatUI: Types message & clicks Send
    ChatUI->>ChatUI: showLoading()
    ChatUI->>ChatService: sendMessage(msg, yaml, selection)
    ChatService->>Flask: POST /api/chat
    Flask->>LLM: chat(message, yaml, component)

    LLM->>LLM: _build_system_prompt()<br/>(includes LLM_COMPONENT_GUIDE.md)
    LLM->>LLM: _build_prompt()<br/>(adds YAML context + selection)
    LLM->>Log: Log request
    LLM->>Ollama: client.chat(messages)

    alt Timeout
        Ollama-->>LLM: TimeoutError
        LLM->>Log: Log error
        LLM-->>Flask: {action: "error", error: "timeout"}
    else Success
        Ollama-->>LLM: Response with YAML
        LLM->>LLM: _parse_response()<br/>(extract YAML, validate)
        LLM->>Log: Log response
        LLM-->>Flask: {action, yaml, response, warning?}
    end

    Flask-->>ChatService: JSON Response
    ChatService-->>ChatUI: Result object
    ChatUI->>ChatUI: hideLoading()

    alt Has YAML
        ChatUI->>ChatUI: displayYamlResponse()<br/>(show YAML + Apply button)
        User->>ChatUI: Clicks "Apply Changes"
        ChatUI->>ChatUI: applyYamlChanges()
        ChatUI-->>User: Update Editor → Re-render
    else Error
        ChatUI->>ChatUI: addMessage(error)
    end
```

---

## Selection Event System

```mermaid
flowchart LR
    subgraph Iframe["Preview Iframe"]
        Click["User clicks<br/>component"]
        Bridge["preview_bridge.js"]
    end

    subgraph MainWindow["Main Window"]
        SSRApp["ssr_app.js"]
        SelMgr["SelectionManager"]
        Event["CustomEvent<br/>swift-selection-changed"]

        subgraph Listeners["Event Listeners"]
            ChatUI["Chat UI<br/>updateSelectionIndicator()"]
            PropsPanel["Properties Panel<br/>renderPropertiesPanel()"]
            CompTree["Component Tree<br/>highlightNode()"]
        end
    end

    Click -->|"finds data-component-id"| Bridge
    Bridge -->|"postMessage<br/>COMPONENT_CLICKED"| SSRApp
    SSRApp -->|"dispatch event"| SelMgr
    SelMgr -->|"selectComponent()"| Event

    Event -->|"addEventListener"| ChatUI
    Event -->|"onSelectionChange callback"| PropsPanel
    Event -->|"addEventListener"| CompTree

    SelMgr -->|"postMessage<br/>SET_SELECTION"| Bridge
    Bridge -->|"Add .selected class"| Click
```

---

## SSR Rendering Flow

```mermaid
flowchart TD
    subgraph Input["User Input"]
        YAML["YAML in Editor"]
    end

    subgraph Flask["Flask Server"]
        Route["routes/render.py<br/>POST /render"]
        RendererPy["renderer.py<br/>render_yaml_structure()"]
        BuildTemplate["_build_component_template()<br/>concatenates 28 macro files"]

        subgraph Jinja["Jinja2 Processing"]
            Macros["components/*.html"]
            RenderComp["render_component()"]
            BuildStyles["build_styles()"]
        end

        subgraph Data["Data Sources"]
            Tokens["tokens.yaml"]
            Defaults["config/component_defaults.yaml"]
        end
    end

    subgraph Output["Output"]
        HTML["HTML String"]
        Preview["Iframe Preview"]
    end

    YAML -->|"POST request"| Route
    Route --> RendererPy
    RendererPy --> BuildTemplate
    BuildTemplate --> Macros
    Macros --> RenderComp
    RenderComp --> BuildStyles

    Tokens --> BuildStyles
    Defaults --> RendererPy

    BuildStyles --> HTML
    HTML -->|"Response"| Preview
```

---

## Iframe Communication Protocol

```mermaid
sequenceDiagram
    participant Parent as Main Window<br/>(ssr_app.js)
    participant Iframe as Preview Iframe<br/>(preview_bridge.js)

    Note over Parent,Iframe: Initialization
    Iframe->>Parent: IFRAME_READY
    Parent->>Iframe: IFRAME_READY_ACK

    Note over Parent,Iframe: Content Update
    Parent->>Iframe: UPDATE_CONTENT {html}
    Iframe->>Iframe: Update DOM
    Iframe->>Parent: COMPONENTS_READY {ids[]}

    Note over Parent,Iframe: Selection
    Iframe->>Parent: COMPONENT_CLICKED {id}
    Parent->>Parent: SelectionManager.selectComponent()
    Parent->>Iframe: SET_SELECTION {id}
    Iframe->>Iframe: Add .selected class

    Note over Parent,Iframe: Clear Selection
    Parent->>Iframe: CLEAR_SELECTION
    Iframe->>Iframe: Remove .selected class
```

---

## File Structure Overview

```mermaid
flowchart TD
    subgraph Root["Project Root"]
        CLAUDE["CLAUDE.md"]
        LLMGuide["LLM_COMPONENT_GUIDE.md"]
        Docs["docs/"]
        ExampleTemplates["example_templates/"]
    end

    subgraph SSR["ssr_python/"]
        AppPy["app.py (factory)"]
        ConfigPy["config.py"]
        ExtPy["extensions.py"]
        RendererPy["renderer.py"]
        LLMServicePy["llm_service.py"]
        TokensYAML["tokens.yaml"]

        subgraph Routes["routes/"]
            ViewsBP["views.py"]
            RenderBP["render.py"]
            MetadataBP["metadata.py"]
            ImagesBP["images.py"]
            ChatBP["chat.py"]
        end

        subgraph ConfigDir["config/"]
            CompDefaults["component_defaults.yaml"]
            CompSchemas["component_schemas.yaml"]
            SchemaTokens["schema_tokens.yaml"]
        end

        subgraph Tests["tests/"]
            Conftest["conftest.py"]
            TestRenderer["test_renderer.py"]
            TestRoutes["test_routes.py"]
            TestSecurity["test_security.py"]
        end

        subgraph Templates["templates/"]
            IndexHTML["index.html"]
            PreviewHTML["preview_frame.html"]
            subgraph Components["components/ (28 files)"]
                Assembly["_assembly.html"]
                Utilities["_utilities.html"]
                Dispatcher["_dispatcher.html"]
            end
        end

        subgraph Static["static/"]
            subgraph JS["js/"]
                MainJS["main.js"]
                SSRAppJS["ssr_app.js"]
                PreviewBridgeJS["preview_bridge.js"]
                ChatJS["chat.js"]
                ChatServiceJS["chatService.js"]
                SelectionMgrJS["selectionManager.js"]
                PropsJS["propertiesPanel.js"]
            end

            subgraph CSS["css/"]
                StyleCSS["style.css"]
                ComponentsCSS["components.css"]
                ChatCSS["chat.css"]
            end
        end

        subgraph Logs["logs/"]
            ChatLog["llm_chat.log"]
        end
    end

    AppPy --> ConfigPy
    AppPy --> ExtPy
    AppPy --> Routes
    ChatBP --> LLMServicePy
    LLMServicePy --> LLMGuide
    LLMServicePy --> ChatLog
    RenderBP --> RendererPy
    RendererPy --> Components
    RendererPy --> TokensYAML
    ExtPy --> CompDefaults
    ExtPy --> TokensYAML
```

---

## Data Flow Summary

| Flow | Source | Destination | Method |
|------|--------|-------------|--------|
| YAML → HTML | Editor | Iframe | POST /render → postMessage |
| Selection | Iframe | Chat/Props | postMessage → CustomEvent |
| Chat Request | Chat UI | LLM Service | POST /api/chat |
| LLM Response | Ollama | Chat UI | JSON Response |
| Apply YAML | Chat UI | Editor | Direct DOM update |
| Properties Edit | Props Panel | Editor | YAML manipulation |

---

**Last Updated:** February 13, 2026
