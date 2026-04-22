package com.example.signaturecapture;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.DisplayMetrics;
import android.util.TypedValue;
import android.view.View;

public class SignatureFieldView extends View {
    private static final float FIELD_WIDTH_MM = 60f;
    private static final float FIELD_HEIGHT_MM = 96f;

    private final Paint framePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint bgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint strokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private Bitmap signatureBitmap;
    private Canvas bitmapCanvas;

    private int fieldWidthPx;
    private int fieldHeightPx;

    public SignatureFieldView(Context context) {
        super(context);
        init();
    }

    public SignatureFieldView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public SignatureFieldView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        setFocusable(true);
        setFocusableInTouchMode(true);

        framePaint.setColor(Color.BLACK);
        framePaint.setStyle(Paint.Style.STROKE);
        framePaint.setStrokeWidth(dp(2));

        bgPaint.setColor(Color.WHITE);
        bgPaint.setStyle(Paint.Style.FILL);

        strokePaint.setColor(Color.BLACK);
        strokePaint.setStyle(Paint.Style.STROKE);
        strokePaint.setStrokeWidth(dp(2));
        strokePaint.setStrokeCap(Paint.Cap.ROUND);
        strokePaint.setStrokeJoin(Paint.Join.ROUND);

        computePhysicalSize();
    }

    private void computePhysicalSize() {
        DisplayMetrics dm = getResources().getDisplayMetrics();
        float xdpi = dm.xdpi;
        float ydpi = dm.ydpi;

        fieldWidthPx = Math.round((FIELD_WIDTH_MM / 25.4f) * xdpi);
        fieldHeightPx = Math.round((FIELD_HEIGHT_MM / 25.4f) * ydpi);
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        setMeasuredDimension(fieldWidthPx, fieldHeightPx);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        recreateBitmap(w, h);
    }

    private void recreateBitmap(int w, int h) {
        if (w <= 0 || h <= 0) {
            return;
        }
        if (signatureBitmap != null) {
            signatureBitmap.recycle();
        }
        signatureBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        bitmapCanvas = new Canvas(signatureBitmap);
        bitmapCanvas.drawColor(Color.WHITE);
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawRect(0, 0, getWidth(), getHeight(), bgPaint);
        if (signatureBitmap != null) {
            canvas.drawBitmap(signatureBitmap, 0, 0, null);
        }
        canvas.drawRect(0, 0, getWidth(), getHeight(), framePaint);
    }

    public void drawSegment(float x1, float y1, float x2, float y2) {
        if (bitmapCanvas == null) {
            return;
        }
        bitmapCanvas.drawLine(x1, y1, x2, y2, strokePaint);
        invalidate();
    }

    public void drawPoint(float x, float y) {
        if (bitmapCanvas == null) {
            return;
        }
        bitmapCanvas.drawCircle(x, y, Math.max(1f, strokePaint.getStrokeWidth() / 2f), strokePaint);
        invalidate();
    }

    public void clear() {
        if (bitmapCanvas != null) {
            bitmapCanvas.drawColor(Color.WHITE);
            invalidate();
        }
    }

    public Bitmap getSignatureBitmapCopy() {
        if (signatureBitmap == null) {
            return null;
        }
        return signatureBitmap.copy(Bitmap.Config.ARGB_8888, false);
    }

    public int getFieldWidthPx() {
        return getWidth();
    }

    public int getFieldHeightPx() {
        return getHeight();
    }

    private float dp(int value) {
        return TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, value,
                getResources().getDisplayMetrics());
    }
}
