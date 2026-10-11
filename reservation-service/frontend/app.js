// The API is served from this same origin (see app.main.create_app), so the
// default base URL is empty and requests stay relative. The overrides remain
// for pointing the UI at an API running somewhere else.
const configuredApiUrl = new URLSearchParams(window.location.search).get("api");
const apiBaseUrl = (
  window.SLOTWISE_API_URL || configuredApiUrl || ""
).replace(/\/$/, "");

const state = { userId: 1, pending: false };
const userSelect = document.querySelector("#user-select");
const errorBox = document.querySelector("#error");
const sessionsBox = document.querySelector("#sessions");
const activeBox = document.querySelector("#active-reservations");
const cancelledBox = document.querySelector("#cancelled-reservations");

async function request(path, init = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-User-ID": String(state.userId),
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

function showError(reason) {
  errorBox.textContent = reason instanceof Error ? reason.message : String(reason);
  errorBox.hidden = false;
}

function clearError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function syncActionButtons() {
  for (const button of sessionsBox.querySelectorAll("button[data-session-id]")) {
    button.disabled = state.pending || button.dataset.availableSlots === "0";
  }

  for (const button of activeBox.querySelectorAll("button[data-reservation-id]")) {
    button.disabled = state.pending;
  }
}

function renderSessions(rows) {
  sessionsBox.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = "No upcoming sessions.";
    sessionsBox.append(empty);
    return;
  }

  for (const session of rows) {
    const card = document.createElement("article");
    card.className = "card";

    const date = document.createElement("p");
    date.className = "eyebrow";
    date.textContent = new Date(session.starts_at).toLocaleString();

    const title = document.createElement("h3");
    title.textContent = session.title;

    const capacity = document.createElement("p");
    capacity.textContent = `${session.available_slots} of ${session.capacity} places available`;

    const reserveButton = document.createElement("button");
    reserveButton.type = "button";
    reserveButton.dataset.sessionId = session.id;
    reserveButton.dataset.availableSlots = String(session.available_slots);
    reserveButton.textContent = session.available_slots === 0 ? "Full" : "Reserve";
    reserveButton.disabled = session.available_slots === 0;

    card.append(date, title, capacity, reserveButton);
    sessionsBox.append(card);
  }
}

function renderReservations(box, rows, canCancel) {
  box.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("li");
    empty.className = "muted";
    empty.textContent = "Nothing here.";
    box.append(empty);
    return;
  }

  for (const reservation of rows) {
    const row = document.createElement("li");
    row.textContent = `Reservation #${reservation.id}, session ${reservation.session_id}`;
    if (canCancel) {
      const cancelButton = document.createElement("button");
      cancelButton.type = "button";
      cancelButton.className = "link";
      cancelButton.dataset.reservationId = reservation.id;
      cancelButton.textContent = "Cancel";
      row.append(cancelButton);
    }
    box.append(row);
  }
}

async function refresh() {
  clearError();
  sessionsBox.innerHTML = '<p class="muted">Loading sessions...</p>';
  activeBox.innerHTML = '<li class="muted">Loading...</li>';
  cancelledBox.innerHTML = '<li class="muted">Loading...</li>';

  try {
    const [sessions, active, cancelled] = await Promise.all([
      request("/api/sessions"),
      request("/api/reservations/me?status=active"),
      request("/api/reservations/me?status=cancelled"),
    ]);
    renderSessions(sessions);
    renderReservations(activeBox, active, true);
    renderReservations(cancelledBox, cancelled, false);
    syncActionButtons();
  } catch (reason) {
    showError(reason);
    sessionsBox.innerHTML = '<p class="muted">Unable to load sessions.</p>';
    activeBox.innerHTML = '<li class="muted">Unable to load reservations.</li>';
    cancelledBox.replaceChildren();
  }
}

async function runAction(action) {
  if (state.pending) return;
  state.pending = true;
  syncActionButtons();
  try {
    await action();
    await refresh();
  } catch (reason) {
    await refresh();
    showError(reason);
  } finally {
    state.pending = false;
    syncActionButtons();
  }
}

userSelect.addEventListener("change", () => {
  state.userId = Number(userSelect.value);
  void refresh();
});

sessionsBox.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-session-id]");
  if (!button) return;
  void runAction(() => request(`/api/sessions/${button.dataset.sessionId}/reservations`, { method: "POST" }));
});

activeBox.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-reservation-id]");
  if (!button) return;
  void runAction(() => request(`/api/reservations/${button.dataset.reservationId}/cancel`, { method: "POST" }));
});

void refresh();
