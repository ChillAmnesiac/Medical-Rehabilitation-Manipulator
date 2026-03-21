package com.rehab.robotarm.data.database.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.rehab.robotarm.data.database.entity.RehabAssessment;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Float;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class RehabAssessmentDao_Impl implements RehabAssessmentDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<RehabAssessment> __insertionAdapterOfRehabAssessment;

  private final EntityDeletionOrUpdateAdapter<RehabAssessment> __deletionAdapterOfRehabAssessment;

  private final SharedSQLiteStatement __preparedStmtOfDeleteBySession;

  public RehabAssessmentDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfRehabAssessment = new EntityInsertionAdapter<RehabAssessment>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `rehab_assessments` (`id`,`sessionId`,`smoothness`,`rangeOfMotion`,`strength`,`overallScore`,`recommendation`,`cloudRecommendation`,`timestamp`) VALUES (?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final RehabAssessment entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getSessionId());
        statement.bindDouble(3, entity.getSmoothness());
        statement.bindDouble(4, entity.getRangeOfMotion());
        statement.bindDouble(5, entity.getStrength());
        statement.bindDouble(6, entity.getOverallScore());
        statement.bindString(7, entity.getRecommendation());
        if (entity.getCloudRecommendation() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getCloudRecommendation());
        }
        statement.bindLong(9, entity.getTimestamp());
      }
    };
    this.__deletionAdapterOfRehabAssessment = new EntityDeletionOrUpdateAdapter<RehabAssessment>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `rehab_assessments` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final RehabAssessment entity) {
        statement.bindString(1, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteBySession = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM rehab_assessments WHERE sessionId = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final RehabAssessment assessment,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfRehabAssessment.insert(assessment);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object delete(final RehabAssessment assessment,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfRehabAssessment.handle(assessment);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteBySession(final String sessionId,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteBySession.acquire();
        int _argIndex = 1;
        _stmt.bindString(_argIndex, sessionId);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfDeleteBySession.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object getBySession(final String sessionId,
      final Continuation<? super RehabAssessment> $completion) {
    final String _sql = "SELECT * FROM rehab_assessments WHERE sessionId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<RehabAssessment>() {
      @Override
      @Nullable
      public RehabAssessment call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfSmoothness = CursorUtil.getColumnIndexOrThrow(_cursor, "smoothness");
          final int _cursorIndexOfRangeOfMotion = CursorUtil.getColumnIndexOrThrow(_cursor, "rangeOfMotion");
          final int _cursorIndexOfStrength = CursorUtil.getColumnIndexOrThrow(_cursor, "strength");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "recommendation");
          final int _cursorIndexOfCloudRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "cloudRecommendation");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final RehabAssessment _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpSessionId;
            _tmpSessionId = _cursor.getString(_cursorIndexOfSessionId);
            final float _tmpSmoothness;
            _tmpSmoothness = _cursor.getFloat(_cursorIndexOfSmoothness);
            final float _tmpRangeOfMotion;
            _tmpRangeOfMotion = _cursor.getFloat(_cursorIndexOfRangeOfMotion);
            final float _tmpStrength;
            _tmpStrength = _cursor.getFloat(_cursorIndexOfStrength);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final String _tmpRecommendation;
            _tmpRecommendation = _cursor.getString(_cursorIndexOfRecommendation);
            final String _tmpCloudRecommendation;
            if (_cursor.isNull(_cursorIndexOfCloudRecommendation)) {
              _tmpCloudRecommendation = null;
            } else {
              _tmpCloudRecommendation = _cursor.getString(_cursorIndexOfCloudRecommendation);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            _result = new RehabAssessment(_tmpId,_tmpSessionId,_tmpSmoothness,_tmpRangeOfMotion,_tmpStrength,_tmpOverallScore,_tmpRecommendation,_tmpCloudRecommendation,_tmpTimestamp);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Flow<RehabAssessment> getBySessionFlow(final String sessionId) {
    final String _sql = "SELECT * FROM rehab_assessments WHERE sessionId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"rehab_assessments"}, new Callable<RehabAssessment>() {
      @Override
      @Nullable
      public RehabAssessment call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfSmoothness = CursorUtil.getColumnIndexOrThrow(_cursor, "smoothness");
          final int _cursorIndexOfRangeOfMotion = CursorUtil.getColumnIndexOrThrow(_cursor, "rangeOfMotion");
          final int _cursorIndexOfStrength = CursorUtil.getColumnIndexOrThrow(_cursor, "strength");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "recommendation");
          final int _cursorIndexOfCloudRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "cloudRecommendation");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final RehabAssessment _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpSessionId;
            _tmpSessionId = _cursor.getString(_cursorIndexOfSessionId);
            final float _tmpSmoothness;
            _tmpSmoothness = _cursor.getFloat(_cursorIndexOfSmoothness);
            final float _tmpRangeOfMotion;
            _tmpRangeOfMotion = _cursor.getFloat(_cursorIndexOfRangeOfMotion);
            final float _tmpStrength;
            _tmpStrength = _cursor.getFloat(_cursorIndexOfStrength);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final String _tmpRecommendation;
            _tmpRecommendation = _cursor.getString(_cursorIndexOfRecommendation);
            final String _tmpCloudRecommendation;
            if (_cursor.isNull(_cursorIndexOfCloudRecommendation)) {
              _tmpCloudRecommendation = null;
            } else {
              _tmpCloudRecommendation = _cursor.getString(_cursorIndexOfCloudRecommendation);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            _result = new RehabAssessment(_tmpId,_tmpSessionId,_tmpSmoothness,_tmpRangeOfMotion,_tmpStrength,_tmpOverallScore,_tmpRecommendation,_tmpCloudRecommendation,_tmpTimestamp);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Flow<List<RehabAssessment>> getRecentAssessments(final int limit) {
    final String _sql = "SELECT * FROM rehab_assessments ORDER BY timestamp DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, limit);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"rehab_assessments"}, new Callable<List<RehabAssessment>>() {
      @Override
      @NonNull
      public List<RehabAssessment> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfSmoothness = CursorUtil.getColumnIndexOrThrow(_cursor, "smoothness");
          final int _cursorIndexOfRangeOfMotion = CursorUtil.getColumnIndexOrThrow(_cursor, "rangeOfMotion");
          final int _cursorIndexOfStrength = CursorUtil.getColumnIndexOrThrow(_cursor, "strength");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "recommendation");
          final int _cursorIndexOfCloudRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "cloudRecommendation");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final List<RehabAssessment> _result = new ArrayList<RehabAssessment>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final RehabAssessment _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpSessionId;
            _tmpSessionId = _cursor.getString(_cursorIndexOfSessionId);
            final float _tmpSmoothness;
            _tmpSmoothness = _cursor.getFloat(_cursorIndexOfSmoothness);
            final float _tmpRangeOfMotion;
            _tmpRangeOfMotion = _cursor.getFloat(_cursorIndexOfRangeOfMotion);
            final float _tmpStrength;
            _tmpStrength = _cursor.getFloat(_cursorIndexOfStrength);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final String _tmpRecommendation;
            _tmpRecommendation = _cursor.getString(_cursorIndexOfRecommendation);
            final String _tmpCloudRecommendation;
            if (_cursor.isNull(_cursorIndexOfCloudRecommendation)) {
              _tmpCloudRecommendation = null;
            } else {
              _tmpCloudRecommendation = _cursor.getString(_cursorIndexOfCloudRecommendation);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            _item = new RehabAssessment(_tmpId,_tmpSessionId,_tmpSmoothness,_tmpRangeOfMotion,_tmpStrength,_tmpOverallScore,_tmpRecommendation,_tmpCloudRecommendation,_tmpTimestamp);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Flow<List<RehabAssessment>> getAllAssessments() {
    final String _sql = "SELECT * FROM rehab_assessments ORDER BY timestamp DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"rehab_assessments"}, new Callable<List<RehabAssessment>>() {
      @Override
      @NonNull
      public List<RehabAssessment> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfSmoothness = CursorUtil.getColumnIndexOrThrow(_cursor, "smoothness");
          final int _cursorIndexOfRangeOfMotion = CursorUtil.getColumnIndexOrThrow(_cursor, "rangeOfMotion");
          final int _cursorIndexOfStrength = CursorUtil.getColumnIndexOrThrow(_cursor, "strength");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "recommendation");
          final int _cursorIndexOfCloudRecommendation = CursorUtil.getColumnIndexOrThrow(_cursor, "cloudRecommendation");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final List<RehabAssessment> _result = new ArrayList<RehabAssessment>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final RehabAssessment _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpSessionId;
            _tmpSessionId = _cursor.getString(_cursorIndexOfSessionId);
            final float _tmpSmoothness;
            _tmpSmoothness = _cursor.getFloat(_cursorIndexOfSmoothness);
            final float _tmpRangeOfMotion;
            _tmpRangeOfMotion = _cursor.getFloat(_cursorIndexOfRangeOfMotion);
            final float _tmpStrength;
            _tmpStrength = _cursor.getFloat(_cursorIndexOfStrength);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final String _tmpRecommendation;
            _tmpRecommendation = _cursor.getString(_cursorIndexOfRecommendation);
            final String _tmpCloudRecommendation;
            if (_cursor.isNull(_cursorIndexOfCloudRecommendation)) {
              _tmpCloudRecommendation = null;
            } else {
              _tmpCloudRecommendation = _cursor.getString(_cursorIndexOfCloudRecommendation);
            }
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            _item = new RehabAssessment(_tmpId,_tmpSessionId,_tmpSmoothness,_tmpRangeOfMotion,_tmpStrength,_tmpOverallScore,_tmpRecommendation,_tmpCloudRecommendation,_tmpTimestamp);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object getAverageScore(final long startTime,
      final Continuation<? super Float> $completion) {
    final String _sql = "SELECT AVG(overallScore) FROM rehab_assessments WHERE timestamp >= ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, startTime);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Float>() {
      @Override
      @Nullable
      public Float call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Float _result;
          if (_cursor.moveToFirst()) {
            final Float _tmp;
            if (_cursor.isNull(0)) {
              _tmp = null;
            } else {
              _tmp = _cursor.getFloat(0);
            }
            _result = _tmp;
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
