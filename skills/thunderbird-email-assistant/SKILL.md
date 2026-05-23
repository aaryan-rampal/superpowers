---
name: thunderbird-email-assistant
description: Use when handling email for Aaryan through Thunderbird MCP.
---

# Thunderbird Email Assistant

## Core Rule

Email actions are identity-sensitive. Aaryan uses many accounts and compartmentalizes
digital profiles. Never assume the sender identity is incidental.

## Default Flow

1. Find context with Thunderbird MCP when useful:
   - `listAccounts` to inspect available identities.
   - `searchContacts` and `searchMessages` to find recipients and prior threads.
   - `getMessage` to confirm thread context before replying.
2. Infer a likely sender only from evidence:
   - Prior messages in the same thread.
   - The account that received the original message.
   - The persona implied by the recipient or topic.
3. Show the proposed draft in the conversation first.
4. Ask for approval before creating a Thunderbird draft or sending.
5. If the user does not explicitly say "send", default to a draft.

## Sender Identity

- Always confirm the sender account before saving or sending unless the user already named it.
- If replying to an existing thread, prefer the identity used in that thread.
- If starting a new message, state the inferred sender and why.
- If the context is ambiguous, ask before touching Thunderbird compose tools.

Common account clues:

- UBC administration, advising, tuition, accessibility, coursework: likely
  `arampa01@student.ubc.ca`, but confirm before action.
- Threads previously handled from `r.aaryan2704@gmail.com`: use that identity only when
  the thread evidence supports it and confirm before action.
- Other personal, alias, or niche accounts: do not guess silently.

## Drafting and Sending

- "Draft an email" means show text in the conversation first.
- "Save a draft" means use Thunderbird only after the user approves the shown text.
- "Send it" after approving a shown draft is explicit permission to send that exact content.
- Do not use `skipReview: true` unless the user has approved the final text and explicitly
  asked to send.
- For new approved drafts, use `saveDraft`.
- For approved direct sends, use `sendMail` or `replyToMessage` as appropriate.
- For replies where thread continuity matters, prefer `replyToMessage`; otherwise explain the
  tradeoff before using an unthreaded `saveDraft`.

## Message Style

- Default sign-off:
  ```text
  Regards,
  Aaryan
  ```
- Use `Aaryan Rampal` only for very formal messages.
- Add extra identity context such as `UBC` or `Computer Science` rarely, mainly for professors
  or work-related messages where that context helps.

## Mail Reading

- Use concise digests by default, not raw body dumps.
- Deduplicate Gmail results that appear in Inbox, Important, and All Mail.
- Search narrowly first: recipient, sender, subject, date window, or exact phrase.
- Read full bodies only for messages needed to answer the user or draft accurately.
- Do not expose sensitive details unless they are needed for the task.

## Recipient Safety

- Verify recipients from contacts or prior messages when possible.
- Do not send to `noreply` addresses unless the user explicitly asks.
- For institutional contacts, prefer evidence from signatures or prior successful threads.
- Include student number, account ID, or other identifiers only when relevant and already known
  from local evidence or supplied by the user.

## Calendar, Tasks, and Contacts

- Calendar, task, contact, filter, folder, and bulk message operations are write actions.
- For write actions, describe the intended change first and wait for approval unless the user
  explicitly asked for that exact action.
- Bulk archive, delete, move, tag, filter, or folder changes require extra confirmation.

## Failure Handling

- If search returns no results, try one narrower and one broader query before asking the user.
- If Thunderbird folders are stale, mention that IMAP sync may be needed.
- If multiple plausible identities or recipients appear, present the options and ask.
