package com.example.signaturecapture;

import java.util.List;
import java.util.Locale;

public class CsvWriter {
    public static String buildCsv(List<SignatureSample> samples) {
        StringBuilder sb = new StringBuilder();
        sb.append("timestamp;x;y;pressure;eventType;tilt;orientation;distance\n");
        for (SignatureSample s : samples) {
            sb.append(s.timestamp).append(';')
                    .append(s.x).append(';')
                    .append(s.y).append(';')
                    .append(formatFloat(s.pressure)).append(';')
                    .append(s.eventType).append(';')
                    .append(nullToEmpty(s.tilt)).append(';')
                    .append(nullToEmpty(s.orientation)).append(';')
                    .append(nullToEmpty(s.distance)).append('\n');
        }
        return sb.toString();
    }

    private static String formatFloat(float value) {
        return String.format(Locale.US, "%s", value);
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }
}
