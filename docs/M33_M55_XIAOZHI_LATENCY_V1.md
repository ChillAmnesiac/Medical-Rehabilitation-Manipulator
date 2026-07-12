# M33/M55 XiaoZhi Latency Contract V1

`MSG_TYPE_VOICE_LATENCY` is a low-frequency, one-message-per-turn observation from M55 to M33. It does not alter the existing high-frequency `VOICE_STATUS` cadence and does not create another IPC consumer.

Fields are unsigned millisecond deltas for:

- wake to listen;
- last voice to stop (EOU);
- stop to STT;
- STT to LLM;
- LLM to TTS start;
- TTS start to first accepted audio packet;
- first packet to first successful `sound0` write;
- last voice to first write;
- wake to first write.

Flags are `VALID=0x1`, `REAL_WAKE=0x2`, `MANUAL=0x4`, and `QA_TEXT=0x8`. Missing timestamps produce zero for that segment. The record contains no key, token, transcript, raw audio, CAN data, or motion authority.

Formal motion remains `JointTrajectory -> NanoPi -> M33 -> motor`; M33 remains the final safety authority.
