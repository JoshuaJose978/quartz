---
title: JavaScript State Tree Design
---


State tree design is a way of organizing application state as a single, well-structured tree (usually a plain JavaScript object) instead of having scattered, ad‑hoc variables and nested mutable objects. It’s especially common in frontend app architectures (Redux, MobX-state-tree, Zustand with slices, etc.).

Think of it as:  
**“All the data that describes the current state of the app is in one (or a small number of) structured trees.”**

---

## 1. What is a “state tree”?

A **state tree** is just a nested object that holds your application’s data.

### Example (plain JS)

```js
const state = {
  auth: {
    userId: 'u_123',
    token: 'abc123',
    isLoggedIn: true,
  },
  ui: {
    theme: 'dark',
    sidebarOpen: false,
    activeModal: null,
  },
  entities: {
    users: {
      u_123: { id: 'u_123', name: 'Alice' },
      u_456: { id: 'u_456', name: 'Bob' },
    },
    posts: {
      p_1: { id: 'p_1', authorId: 'u_123', title: 'Hello' },
      p_2: { id: 'p_2', authorId: 'u_456', title: 'World' },
    },
  },
};
```

This single object is the “tree”:

- `auth`, `ui`, `entities` are top-level branches.
- Each branch has more nested data.

The design aspect is about:

- **Choosing the structure** (how you split into branches).
- **Choosing types** (in TS).
- **Rules for updating** (immutably, via actions, etc.).

---

## 2. Why use a state tree?

Common reasons:

1. **Single source of truth** – easier to debug, log, serialize, persist.
2. **Predictability** – if updates are done via clear functions or actions, you know how state changes.
3. **Easier tooling** – time travel debugging, snapshot testing, persistence.
4. **Separation of concerns** – UI reads from state; state updates via actions; logic stays in one place.

---

## 3. TypeScript example of a state tree

```ts
// Define the shape of the entire app state:
type User = {
  id: string;
  name: string;
};

type Post = {
  id: string;
  authorId: string;
  title: string;
};

type AuthState = {
  userId: string | null;
  token: string | null;
  isLoggedIn: boolean;
};

type UIState = {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeModal: string | null;
};

type EntitiesState = {
  users: Record<string, User>;
  posts: Record<string, Post>;
};

type AppState = {
  auth: AuthState;
  ui: UIState;
  entities: EntitiesState;
};

// Example state object:
const initialState: AppState = {
  auth: {
    userId: null,
    token: null,
    isLoggedIn: false,
  },
  ui: {
    theme: 'light',
    sidebarOpen: false,
    activeModal: null,
  },
  entities: {
    users: {},
    posts: {},
  },
};
```

This is the **state tree design**: a typed root `AppState` that describes everything.

---

## 4. Updating a state tree (immutably)

Often, state tree designs recommend **immutable updates** (no in-place mutation) to enable time-travel, undo/redo, etc.

### Example“actions” and “reducers” (Redux-like, but plain TS)

```ts
type Action =
  | { type: 'LOGIN'; payload: { userId: string; token: string } }
  | { type: 'LOGOUT' }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'ADD_USER'; payload: User };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'LOGIN': {
      const { userId, token } = action.payload;
      return {
        ...state,
        auth: {
          userId,
          token,
          isLoggedIn: true,
        },
      };
    }
    case 'LOGOUT': {
      return {
        ...state,
        auth: {
          userId: null,
          token: null,
          isLoggedIn: false,
        },
      };
    }
    case 'TOGGLE_SIDEBAR': {
      return {
        ...state,
        ui: {
          ...state.ui,
          sidebarOpen: !state.ui.sidebarOpen,
        },
      };
    }
    case 'ADD_USER': {
      const user = action.payload;
      return {
        ...state,
        entities: {
          ...state.entities,
          users: {
            ...state.entities.users,
            [user.id]: user,
          },
        },
      };
    }
    default:
      return state;
  }
}
```

Here:

- `AppState` is the tree.
- `reducer` describes **pure** transformations from one tree to another.

---

## 5. Normalized vs deeply nested trees

A state tree can be:

### Deeply nested

```ts
type AppState = {
  currentUser: {
    id: string;
    name: string;
    posts: { id: string; title: string }[];
  };
};
```

This causes problems if you reuse users or posts in many places (duplication, hard updates).

### Normalized (relational style)

More common in “state tree design”:

```ts
type AppState = {
  auth: { userId: string | null; token: string | null; isLoggedIn: boolean };
  entities: {
    users: Record<string, User>;
    posts: Record<string, Post>;
  };
  ui: UIState;
};
```

Then you **compose** data in selectors:

```ts
function selectCurrentUser(state: AppState): User | null {
  const userId = state.auth.userId;
  if (!userId) return null;
  return state.entities.users[userId] ?? null;
}
```

This keeps the tree:

- Easier to update.
- Less duplicative.
- Closer to a database schema.

---

## 6. Things similar to state tree design

Several patterns and libraries use similar ideas, just with different ergonomics:

### 6.1 Redux (classic example of a state tree)

- **Single store**: one big tree.
- Uses reducers and actions.
- Encourages normalization and immutability.

```ts
import { createStore } from 'redux';

const store = createStore(reducer, initialState);

// State is a tree:
const currentState = store.getState();
console.log(currentState.auth.userId);
```

Redux is essentially a formalization of state tree design with tools and conventions.

---

### 6.2 MobX-State-Tree (MST)

MobX itself is about observable state, but **MobX-State-Tree (MST)** explicitly organizes state as a tree of models.

```ts
import { types, Instance } from 'mobx-state-tree';

const UserModel = types.model('User', {
  id: types.identifier,
  name: types.string,
});

const RootStore = types
  .model('RootStore', {
    users: types.map(UserModel),
  })
  .actions(self => ({
    addUser(user: Instance<typeof UserModel>) {
      self.users.set(user.id, user);
    },
  }));

const store = RootStore.create({ users: {} });

store.addUser({ id: 'u_1', name: 'Alice' });
```

Similarities:

- Single tree (`RootStore`).
- Typed structure.
- Explicit updates via actions.
- Snapshots are serializable tree states.

---

### 6.3 Zustand / Jotai / Recoil stores

These libraries also maintain **global or shared state**, often as a structured object, though they’re less strict about a single tree.

Example with Zustand using a state “slice” (part of a tree):

```ts
import create from 'zustand';

type AuthSlice = {
  userId: string | null;
  token: string | null;
  login: (userId: string, token: string) => void;
};

type UISlice = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
};

type StoreState = AuthSlice & UISlice;

const useStore = create<StoreState>((set) => ({
  userId: null,
  token: null,
  login: (userId, token) => set({ userId, token }),

  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

Here, the state is still conceptually one object (a tree), but the library is less opinionated about its shape.

---

### 6.4 Elm Architecture / Flux

- **Flux** introduced unidirectional data flow, with stores that often hold a state tree.
- **Elm architecture** (Model + Update + View) is very close to Redux and state tree design:
  - Model = state tree
  - Update = reducer-like function

---

### 6.5 Domain-driven aggregates / bounded contexts

In backend design, you might organize state as:

- Modules that each have their own state tree.
- A global root that composes them.

Example (Node/TS):

```ts
type CartState = {
  items: { productId: string; quantity: number }[];
};

type UserState = {
  id: string;
  email: string;
};

type BackendState = {
  users: Record<string, UserState>;
  carts: Record<string, CartState>;
};
```

Conceptually similar: a big typed state tree representing domain data.

---

## 7. Practical guidelines for designing a state tree

When designing a state tree in JS/TS:

1. **Define types first**  
   Use TS interfaces/types to model your state up front.

2. **Separate concerns**  
   - `entities` (normalized domain data)
   - `ui` (view-specific state)
   - `session/auth` (user/session info)
   - `config` (static app-level settings)

3. **Normalize collections**  
   Prefer `Record<string, Entity>` over large nested arrays with duplication.

4. **Keep it serializable**  
   Avoid storing non-serializable values (functions, DOM nodes) in the main tree if you rely on persistence, time travel, etc.

5. **Use selectors**  
   Hide the structure behind selector functions, so you can refactor the tree without changing UI code everywhere.

   ```ts
   const selectPostById = (state: AppState, id: string): Post | undefined =>
     state.entities.posts[id];
   ```

6. **Use immutable updates (when needed)**  
   If using libraries like Redux, always return new objects instead of mutating old ones.

---

## 8. Summary

- **State tree design** = organizing app state as a single structured, often typed tree.
- It’s usually:
  - Typed (in TS).
  - Normalized for collections.
  - Updated via explicit, often pure functions (reducers/actions).
- Similar ideas appear in:
  - Redux (classic single state tree).
  - MobX-State-Tree (observable model tree).
  - Zustand, Recoil, Jotai (global/shared state objects).
  - Elm/Flux architectures.
  - Domain-oriented backend state modeling.

If you tell me what kind of project you’re working on (React app, Node backend, etc.), I can sketch a concrete state tree tailored to that use case.
