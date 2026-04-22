package com.example.signaturecapture;

import android.content.Context;
import android.content.SharedPreferences;

public class SessionManager {
    private static final String PREFS = "signature_prefs";
    private static final String KEY_GLOBAL_COUNTER = "global_counter";

    private final SharedPreferences prefs;

    public SessionManager(Context context) {
        prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public synchronized int reserveNextSessionId() {
        int next = prefs.getInt(KEY_GLOBAL_COUNTER, 0) + 1;
        prefs.edit().putInt(KEY_GLOBAL_COUNTER, next).apply();
        return next;
    }
}
