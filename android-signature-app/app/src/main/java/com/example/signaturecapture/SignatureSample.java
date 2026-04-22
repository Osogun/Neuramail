package com.example.signaturecapture;

public class SignatureSample {
    public final long timestamp;
    public final int x;
    public final int y;
    public final float pressure;
    public final String eventType;
    public final String tilt;
    public final String orientation;
    public final String distance;

    public SignatureSample(long timestamp, int x, int y, float pressure, String eventType,
                           String tilt, String orientation, String distance) {
        this.timestamp = timestamp;
        this.x = x;
        this.y = y;
        this.pressure = pressure;
        this.eventType = eventType;
        this.tilt = tilt;
        this.orientation = orientation;
        this.distance = distance;
    }
}
