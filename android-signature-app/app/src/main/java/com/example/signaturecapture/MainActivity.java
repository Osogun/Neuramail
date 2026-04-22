package com.example.signaturecapture;

import android.content.ContentResolver;
import android.content.pm.PackageManager;
import android.content.ContentValues;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {
    private SignatureFieldView signatureFieldView;
    private final List<SignatureSample> samples = new ArrayList<>();

    private final ExecutorService ioExecutor = Executors.newSingleThreadExecutor();

    private SessionManager sessionManager;
    private Integer activeSessionId = null;
    private boolean hasStylusContactInSession = false;

    private boolean hasLastDrawPoint = false;
    private float lastDrawX;
    private float lastDrawY;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (!isSamsungStylusDevice()) {
            Toast.makeText(this, getString(R.string.unsupported_device), Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        sessionManager = new SessionManager(this);

        signatureFieldView = findViewById(R.id.signatureFieldView);
        Button btnNew = findViewById(R.id.btnNew);
        Button btnSavePng = findViewById(R.id.btnSavePng);
        Button btnSaveCsv = findViewById(R.id.btnSaveCsv);

        signatureFieldView.setOnTouchListener((v, event) -> handleMotionEvent(event));
        signatureFieldView.setOnHoverListener((v, event) -> handleMotionEvent(event));

        btnNew.setOnClickListener(v -> onNewSignature());
        btnSavePng.setOnClickListener(v -> onSavePng());
        btnSaveCsv.setOnClickListener(v -> onSaveCsv());
    }

    private boolean isSamsungStylusDevice() {
        boolean samsung = Build.MANUFACTURER != null
                && Build.MANUFACTURER.toLowerCase(Locale.US).contains("samsung");
        PackageManager pm = getPackageManager();
        boolean spenFeature = pm.hasSystemFeature("com.sec.feature.spen_usp")
                || pm.hasSystemFeature("com.samsung.android.sdk.pen.feature.basic_spen");
        return samsung && spenFeature;
    }

    private boolean handleMotionEvent(MotionEvent event) {
        if (!isStylus(event)) {
            return false;
        }

        float x = event.getX();
        float y = event.getY();

        boolean inside = isInsideField(x, y);
        int action = event.getActionMasked();

        if (!inside && (action == MotionEvent.ACTION_HOVER_MOVE
                || action == MotionEvent.ACTION_HOVER_ENTER
                || action == MotionEvent.ACTION_HOVER_EXIT
                || action == MotionEvent.ACTION_MOVE
                || action == MotionEvent.ACTION_DOWN)) {
            return true;
        }

        if (!inside && action == MotionEvent.ACTION_UP) {
            hasLastDrawPoint = false;
            return true;
        }

        switch (action) {
            case MotionEvent.ACTION_DOWN:
                ensureSessionAssigned();
                hasStylusContactInSession = true;
                handleDown(event, x, y);
                break;
            case MotionEvent.ACTION_MOVE:
                handleMove(event);
                break;
            case MotionEvent.ACTION_UP:
                handleUp(event, x, y);
                hasLastDrawPoint = false;
                break;
            case MotionEvent.ACTION_HOVER_ENTER:
                addSample(event, x, y, "HOVER_ENTER");
                break;
            case MotionEvent.ACTION_HOVER_MOVE:
                addSample(event, x, y, "HOVER_MOVE");
                break;
            case MotionEvent.ACTION_HOVER_EXIT:
                addSample(event, x, y, "HOVER_EXIT");
                break;
            default:
                break;
        }
        return true;
    }

    private boolean isStylus(MotionEvent event) {
        return event.getToolType(0) == MotionEvent.TOOL_TYPE_STYLUS;
    }

    private boolean isInsideField(float x, float y) {
        return x >= 0 && x <= signatureFieldView.getWidth() && y >= 0 && y <= signatureFieldView.getHeight();
    }

    private void handleDown(MotionEvent event, float x, float y) {
        addSample(event, x, y, "DOWN");
        signatureFieldView.drawPoint(x, y);
        lastDrawX = x;
        lastDrawY = y;
        hasLastDrawPoint = true;
    }

    private void handleMove(MotionEvent event) {
        int historySize = event.getHistorySize();

        for (int i = 0; i < historySize; i++) {
            float hx = event.getHistoricalX(i);
            float hy = event.getHistoricalY(i);
            if (!isInsideField(hx, hy)) {
                continue;
            }
            addHistoricalSample(event, i, hx, hy, "MOVE_HIST");
            if (hasLastDrawPoint) {
                signatureFieldView.drawSegment(lastDrawX, lastDrawY, hx, hy);
            } else {
                signatureFieldView.drawPoint(hx, hy);
            }
            lastDrawX = hx;
            lastDrawY = hy;
            hasLastDrawPoint = true;
        }

        float x = event.getX();
        float y = event.getY();
        if (!isInsideField(x, y)) {
            return;
        }

        addSample(event, x, y, "MOVE");
        if (hasLastDrawPoint) {
            signatureFieldView.drawSegment(lastDrawX, lastDrawY, x, y);
        } else {
            signatureFieldView.drawPoint(x, y);
        }
        lastDrawX = x;
        lastDrawY = y;
        hasLastDrawPoint = true;
    }

    private void handleUp(MotionEvent event, float x, float y) {
        addSample(event, x, y, "UP");
    }

    private void addHistoricalSample(MotionEvent event, int historyIndex, float x, float y, String eventType) {
        int xScaled = scaleX(x);
        int yScaled = scaleY(y);

        float pressure = 0f;
        if (event.getHistorySize() > historyIndex) {
            pressure = event.getHistoricalPressure(historyIndex);
        }

        String tilt = hasAxis(event, MotionEvent.AXIS_TILT)
                ? formatFloat(event.getHistoricalAxisValue(MotionEvent.AXIS_TILT, historyIndex)) : "";
        String orientation = hasAxis(event, MotionEvent.AXIS_ORIENTATION)
                ? formatFloat(event.getHistoricalAxisValue(MotionEvent.AXIS_ORIENTATION, historyIndex)) : "";
        String distance = hasAxis(event, MotionEvent.AXIS_DISTANCE)
                ? formatFloat(event.getHistoricalAxisValue(MotionEvent.AXIS_DISTANCE, historyIndex)) : "";

        samples.add(new SignatureSample(
                event.getHistoricalEventTime(historyIndex),
                xScaled,
                yScaled,
                pressure,
                eventType,
                tilt,
                orientation,
                distance
        ));
    }

    private void addSample(MotionEvent event, float x, float y, String eventType) {
        int xScaled = scaleX(x);
        int yScaled = scaleY(y);

        float pressure = event.getPressure();
        if (pressure < 0f) {
            pressure = 0f;
        }

        String tilt = hasAxis(event, MotionEvent.AXIS_TILT)
                ? formatFloat(event.getAxisValue(MotionEvent.AXIS_TILT)) : "";
        String orientation = hasAxis(event, MotionEvent.AXIS_ORIENTATION)
                ? formatFloat(event.getAxisValue(MotionEvent.AXIS_ORIENTATION)) : "";
        String distance = hasAxis(event, MotionEvent.AXIS_DISTANCE)
                ? formatFloat(event.getAxisValue(MotionEvent.AXIS_DISTANCE)) : "";

        samples.add(new SignatureSample(
                event.getEventTime(),
                xScaled,
                yScaled,
                pressure,
                eventType,
                tilt,
                orientation,
                distance
        ));
    }

    private boolean hasAxis(MotionEvent event, int axis) {
        InputDevice device = event.getDevice();
        return device != null && device.getMotionRange(axis) != null;
    }

    private int scaleX(float xLocal) {
        return Math.round((xLocal / Math.max(1, signatureFieldView.getFieldWidthPx())) * 6000f);
    }

    private int scaleY(float yFromTop) {
        float yLocal = signatureFieldView.getFieldHeightPx() - yFromTop;
        return Math.round((yLocal / Math.max(1, signatureFieldView.getFieldHeightPx())) * 9600f);
    }

    private String formatFloat(float value) {
        return String.format(Locale.US, "%s", value);
    }

    private void ensureSessionAssigned() {
        if (activeSessionId == null) {
            activeSessionId = sessionManager.reserveNextSessionId();
        }
    }

    private void onNewSignature() {
        signatureFieldView.clear();
        samples.clear();
        hasStylusContactInSession = false;
        hasLastDrawPoint = false;
        activeSessionId = null;
    }

    private void onSavePng() {
        if (!hasStylusContactInSession || activeSessionId == null) {
            Toast.makeText(this, getString(R.string.nothing_to_save), Toast.LENGTH_SHORT).show();
            return;
        }

        Bitmap bitmap = signatureFieldView.getSignatureBitmapCopy();
        if (bitmap == null) {
            Toast.makeText(this, getString(R.string.nothing_to_save), Toast.LENGTH_SHORT).show();
            return;
        }

        int sessionId = activeSessionId;
        ioExecutor.execute(() -> {
            boolean ok = saveBitmapPng(bitmap, "signature" + sessionId + ".png");
            runOnUiThread(() -> {
                if (ok) {
                    Toast.makeText(this, getString(R.string.saved_png), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }

    private void onSaveCsv() {
        if (!hasStylusContactInSession || activeSessionId == null || samples.isEmpty()) {
            return;
        }

        String csv = CsvWriter.buildCsv(samples);
        int sessionId = activeSessionId;

        ioExecutor.execute(() -> {
            boolean ok = saveTextCsv(csv, "signature" + sessionId + ".csv");
            runOnUiThread(() -> {
                if (ok) {
                    Toast.makeText(this, getString(R.string.saved_csv), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }

    private boolean saveBitmapPng(Bitmap bitmap, String fileName) {
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "image/png");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOCUMENTS + "/SignatureCapture");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);

        ContentResolver resolver = getContentResolver();
        Uri uri = resolver.insert(MediaStore.Files.getContentUri("external"), values);
        if (uri == null) {
            return false;
        }

        try (OutputStream os = resolver.openOutputStream(uri)) {
            if (os == null) {
                return false;
            }
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, os);
        } catch (IOException e) {
            return false;
        }

        values.clear();
        values.put(MediaStore.MediaColumns.IS_PENDING, 0);
        resolver.update(uri, values, null, null);
        return true;
    }

    private boolean saveTextCsv(String csvText, String fileName) {
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "text/csv");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOCUMENTS + "/SignatureCapture");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);

        ContentResolver resolver = getContentResolver();
        Uri uri = resolver.insert(MediaStore.Files.getContentUri("external"), values);
        if (uri == null) {
            return false;
        }

        try (OutputStream os = resolver.openOutputStream(uri)) {
            if (os == null) {
                return false;
            }
            os.write(csvText.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            return false;
        }

        values.clear();
        values.put(MediaStore.MediaColumns.IS_PENDING, 0);
        resolver.update(uri, values, null, null);
        return true;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        ioExecutor.shutdown();
    }
}
