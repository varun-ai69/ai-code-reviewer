import mongoose from 'mongoose';

// Each document stores the repository context for a single analysis session.
// MongoDB automatically removes expired documents via the TTL index on createdAt
// (expireAfterSeconds: 1800 = 30 minutes), which replaces the previous in-process
// setInterval cleanup that ran on the repoContexts Map.
const sessionSchema = new mongoose.Schema({
  sessionId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  repoUrl: {
    type: String,
    required: true,
  },
  repoName: {
    type: String,
    required: true,
  },
  // File list is stored as an array of subdocuments {name, content}.
  // _id generation is disabled on subdocuments to keep the stored size smaller.
  files: {
    type: [
      {
        _id: false,
        name: { type: String, required: true },
        content: { type: String, required: true },
      },
    ],
    default: [],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// TTL index: MongoDB removes the document 30 minutes after createdAt.
// Accessing a session refreshes it by updating createdAt (see index.js).
sessionSchema.index({ createdAt: 1 }, { expireAfterSeconds: 1800 });

export default mongoose.model('Session', sessionSchema);
