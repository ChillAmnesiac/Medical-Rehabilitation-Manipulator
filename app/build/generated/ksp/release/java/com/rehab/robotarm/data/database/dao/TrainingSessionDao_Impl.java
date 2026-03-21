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
import com.rehab.robotarm.data.database.entity.TrainingSession;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Float;
import java.lang.Integer;
import java.lang.Long;
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
public final class TrainingSessionDao_Impl implements TrainingSessionDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TrainingSession> __insertionAdapterOfTrainingSession;

  private final EntityDeletionOrUpdateAdapter<TrainingSession> __deletionAdapterOfTrainingSession;

  private final EntityDeletionOrUpdateAdapter<TrainingSession> __updateAdapterOfTrainingSession;

  private final SharedSQLiteStatement __preparedStmtOfMarkSynced;

  public TrainingSessionDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTrainingSession = new EntityInsertionAdapter<TrainingSession>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `training_sessions` (`id`,`patientId`,`startTime`,`endTime`,`duration`,`mode`,`maxShoulderAngle`,`maxElbowAngle`,`avgHeartRate`,`maxHeartRate`,`avgEmg`,`repetitions`,`overallScore`,`painLevel`,`fatigueLevel`,`notes`,`isSynced`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingSession entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getPatientId());
        statement.bindLong(3, entity.getStartTime());
        statement.bindLong(4, entity.getEndTime());
        statement.bindLong(5, entity.getDuration());
        statement.bindString(6, entity.getMode());
        statement.bindDouble(7, entity.getMaxShoulderAngle());
        statement.bindDouble(8, entity.getMaxElbowAngle());
        statement.bindLong(9, entity.getAvgHeartRate());
        statement.bindLong(10, entity.getMaxHeartRate());
        statement.bindDouble(11, entity.getAvgEmg());
        statement.bindLong(12, entity.getRepetitions());
        statement.bindDouble(13, entity.getOverallScore());
        statement.bindLong(14, entity.getPainLevel());
        statement.bindLong(15, entity.getFatigueLevel());
        statement.bindString(16, entity.getNotes());
        final int _tmp = entity.isSynced() ? 1 : 0;
        statement.bindLong(17, _tmp);
      }
    };
    this.__deletionAdapterOfTrainingSession = new EntityDeletionOrUpdateAdapter<TrainingSession>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `training_sessions` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingSession entity) {
        statement.bindString(1, entity.getId());
      }
    };
    this.__updateAdapterOfTrainingSession = new EntityDeletionOrUpdateAdapter<TrainingSession>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `training_sessions` SET `id` = ?,`patientId` = ?,`startTime` = ?,`endTime` = ?,`duration` = ?,`mode` = ?,`maxShoulderAngle` = ?,`maxElbowAngle` = ?,`avgHeartRate` = ?,`maxHeartRate` = ?,`avgEmg` = ?,`repetitions` = ?,`overallScore` = ?,`painLevel` = ?,`fatigueLevel` = ?,`notes` = ?,`isSynced` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingSession entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getPatientId());
        statement.bindLong(3, entity.getStartTime());
        statement.bindLong(4, entity.getEndTime());
        statement.bindLong(5, entity.getDuration());
        statement.bindString(6, entity.getMode());
        statement.bindDouble(7, entity.getMaxShoulderAngle());
        statement.bindDouble(8, entity.getMaxElbowAngle());
        statement.bindLong(9, entity.getAvgHeartRate());
        statement.bindLong(10, entity.getMaxHeartRate());
        statement.bindDouble(11, entity.getAvgEmg());
        statement.bindLong(12, entity.getRepetitions());
        statement.bindDouble(13, entity.getOverallScore());
        statement.bindLong(14, entity.getPainLevel());
        statement.bindLong(15, entity.getFatigueLevel());
        statement.bindString(16, entity.getNotes());
        final int _tmp = entity.isSynced() ? 1 : 0;
        statement.bindLong(17, _tmp);
        statement.bindString(18, entity.getId());
      }
    };
    this.__preparedStmtOfMarkSynced = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE training_sessions SET isSynced = 1 WHERE id = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insertSession(final TrainingSession session,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfTrainingSession.insertAndReturnId(session);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteSession(final TrainingSession session,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfTrainingSession.handle(session);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateSession(final TrainingSession session,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfTrainingSession.handle(session);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object markSynced(final String sessionId, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfMarkSynced.acquire();
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
          __preparedStmtOfMarkSynced.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<TrainingSession>> getSessionsByPatient(final String patientId) {
    final String _sql = "SELECT * FROM training_sessions WHERE patientId = ? ORDER BY startTime DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"training_sessions"}, new Callable<List<TrainingSession>>() {
      @Override
      @NonNull
      public List<TrainingSession> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "startTime");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "endTime");
          final int _cursorIndexOfDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "duration");
          final int _cursorIndexOfMode = CursorUtil.getColumnIndexOrThrow(_cursor, "mode");
          final int _cursorIndexOfMaxShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxShoulderAngle");
          final int _cursorIndexOfMaxElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxElbowAngle");
          final int _cursorIndexOfAvgHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "avgHeartRate");
          final int _cursorIndexOfMaxHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "maxHeartRate");
          final int _cursorIndexOfAvgEmg = CursorUtil.getColumnIndexOrThrow(_cursor, "avgEmg");
          final int _cursorIndexOfRepetitions = CursorUtil.getColumnIndexOrThrow(_cursor, "repetitions");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfPainLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "painLevel");
          final int _cursorIndexOfFatigueLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "fatigueLevel");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfIsSynced = CursorUtil.getColumnIndexOrThrow(_cursor, "isSynced");
          final List<TrainingSession> _result = new ArrayList<TrainingSession>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingSession _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final long _tmpEndTime;
            _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            final long _tmpDuration;
            _tmpDuration = _cursor.getLong(_cursorIndexOfDuration);
            final String _tmpMode;
            _tmpMode = _cursor.getString(_cursorIndexOfMode);
            final float _tmpMaxShoulderAngle;
            _tmpMaxShoulderAngle = _cursor.getFloat(_cursorIndexOfMaxShoulderAngle);
            final float _tmpMaxElbowAngle;
            _tmpMaxElbowAngle = _cursor.getFloat(_cursorIndexOfMaxElbowAngle);
            final int _tmpAvgHeartRate;
            _tmpAvgHeartRate = _cursor.getInt(_cursorIndexOfAvgHeartRate);
            final int _tmpMaxHeartRate;
            _tmpMaxHeartRate = _cursor.getInt(_cursorIndexOfMaxHeartRate);
            final float _tmpAvgEmg;
            _tmpAvgEmg = _cursor.getFloat(_cursorIndexOfAvgEmg);
            final int _tmpRepetitions;
            _tmpRepetitions = _cursor.getInt(_cursorIndexOfRepetitions);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final int _tmpPainLevel;
            _tmpPainLevel = _cursor.getInt(_cursorIndexOfPainLevel);
            final int _tmpFatigueLevel;
            _tmpFatigueLevel = _cursor.getInt(_cursorIndexOfFatigueLevel);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final boolean _tmpIsSynced;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSynced);
            _tmpIsSynced = _tmp != 0;
            _item = new TrainingSession(_tmpId,_tmpPatientId,_tmpStartTime,_tmpEndTime,_tmpDuration,_tmpMode,_tmpMaxShoulderAngle,_tmpMaxElbowAngle,_tmpAvgHeartRate,_tmpMaxHeartRate,_tmpAvgEmg,_tmpRepetitions,_tmpOverallScore,_tmpPainLevel,_tmpFatigueLevel,_tmpNotes,_tmpIsSynced);
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
  public Object getSessionById(final String sessionId,
      final Continuation<? super TrainingSession> $completion) {
    final String _sql = "SELECT * FROM training_sessions WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<TrainingSession>() {
      @Override
      @Nullable
      public TrainingSession call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "startTime");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "endTime");
          final int _cursorIndexOfDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "duration");
          final int _cursorIndexOfMode = CursorUtil.getColumnIndexOrThrow(_cursor, "mode");
          final int _cursorIndexOfMaxShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxShoulderAngle");
          final int _cursorIndexOfMaxElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxElbowAngle");
          final int _cursorIndexOfAvgHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "avgHeartRate");
          final int _cursorIndexOfMaxHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "maxHeartRate");
          final int _cursorIndexOfAvgEmg = CursorUtil.getColumnIndexOrThrow(_cursor, "avgEmg");
          final int _cursorIndexOfRepetitions = CursorUtil.getColumnIndexOrThrow(_cursor, "repetitions");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfPainLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "painLevel");
          final int _cursorIndexOfFatigueLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "fatigueLevel");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfIsSynced = CursorUtil.getColumnIndexOrThrow(_cursor, "isSynced");
          final TrainingSession _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final long _tmpEndTime;
            _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            final long _tmpDuration;
            _tmpDuration = _cursor.getLong(_cursorIndexOfDuration);
            final String _tmpMode;
            _tmpMode = _cursor.getString(_cursorIndexOfMode);
            final float _tmpMaxShoulderAngle;
            _tmpMaxShoulderAngle = _cursor.getFloat(_cursorIndexOfMaxShoulderAngle);
            final float _tmpMaxElbowAngle;
            _tmpMaxElbowAngle = _cursor.getFloat(_cursorIndexOfMaxElbowAngle);
            final int _tmpAvgHeartRate;
            _tmpAvgHeartRate = _cursor.getInt(_cursorIndexOfAvgHeartRate);
            final int _tmpMaxHeartRate;
            _tmpMaxHeartRate = _cursor.getInt(_cursorIndexOfMaxHeartRate);
            final float _tmpAvgEmg;
            _tmpAvgEmg = _cursor.getFloat(_cursorIndexOfAvgEmg);
            final int _tmpRepetitions;
            _tmpRepetitions = _cursor.getInt(_cursorIndexOfRepetitions);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final int _tmpPainLevel;
            _tmpPainLevel = _cursor.getInt(_cursorIndexOfPainLevel);
            final int _tmpFatigueLevel;
            _tmpFatigueLevel = _cursor.getInt(_cursorIndexOfFatigueLevel);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final boolean _tmpIsSynced;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSynced);
            _tmpIsSynced = _tmp != 0;
            _result = new TrainingSession(_tmpId,_tmpPatientId,_tmpStartTime,_tmpEndTime,_tmpDuration,_tmpMode,_tmpMaxShoulderAngle,_tmpMaxElbowAngle,_tmpAvgHeartRate,_tmpMaxHeartRate,_tmpAvgEmg,_tmpRepetitions,_tmpOverallScore,_tmpPainLevel,_tmpFatigueLevel,_tmpNotes,_tmpIsSynced);
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
  public Object getSessionsInRange(final String patientId, final long startTime, final long endTime,
      final Continuation<? super List<TrainingSession>> $completion) {
    final String _sql = "SELECT * FROM training_sessions WHERE patientId = ? AND startTime >= ? AND startTime <= ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 3);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    _argIndex = 2;
    _statement.bindLong(_argIndex, startTime);
    _argIndex = 3;
    _statement.bindLong(_argIndex, endTime);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<TrainingSession>>() {
      @Override
      @NonNull
      public List<TrainingSession> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "startTime");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "endTime");
          final int _cursorIndexOfDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "duration");
          final int _cursorIndexOfMode = CursorUtil.getColumnIndexOrThrow(_cursor, "mode");
          final int _cursorIndexOfMaxShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxShoulderAngle");
          final int _cursorIndexOfMaxElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxElbowAngle");
          final int _cursorIndexOfAvgHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "avgHeartRate");
          final int _cursorIndexOfMaxHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "maxHeartRate");
          final int _cursorIndexOfAvgEmg = CursorUtil.getColumnIndexOrThrow(_cursor, "avgEmg");
          final int _cursorIndexOfRepetitions = CursorUtil.getColumnIndexOrThrow(_cursor, "repetitions");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfPainLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "painLevel");
          final int _cursorIndexOfFatigueLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "fatigueLevel");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfIsSynced = CursorUtil.getColumnIndexOrThrow(_cursor, "isSynced");
          final List<TrainingSession> _result = new ArrayList<TrainingSession>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingSession _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final long _tmpEndTime;
            _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            final long _tmpDuration;
            _tmpDuration = _cursor.getLong(_cursorIndexOfDuration);
            final String _tmpMode;
            _tmpMode = _cursor.getString(_cursorIndexOfMode);
            final float _tmpMaxShoulderAngle;
            _tmpMaxShoulderAngle = _cursor.getFloat(_cursorIndexOfMaxShoulderAngle);
            final float _tmpMaxElbowAngle;
            _tmpMaxElbowAngle = _cursor.getFloat(_cursorIndexOfMaxElbowAngle);
            final int _tmpAvgHeartRate;
            _tmpAvgHeartRate = _cursor.getInt(_cursorIndexOfAvgHeartRate);
            final int _tmpMaxHeartRate;
            _tmpMaxHeartRate = _cursor.getInt(_cursorIndexOfMaxHeartRate);
            final float _tmpAvgEmg;
            _tmpAvgEmg = _cursor.getFloat(_cursorIndexOfAvgEmg);
            final int _tmpRepetitions;
            _tmpRepetitions = _cursor.getInt(_cursorIndexOfRepetitions);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final int _tmpPainLevel;
            _tmpPainLevel = _cursor.getInt(_cursorIndexOfPainLevel);
            final int _tmpFatigueLevel;
            _tmpFatigueLevel = _cursor.getInt(_cursorIndexOfFatigueLevel);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final boolean _tmpIsSynced;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSynced);
            _tmpIsSynced = _tmp != 0;
            _item = new TrainingSession(_tmpId,_tmpPatientId,_tmpStartTime,_tmpEndTime,_tmpDuration,_tmpMode,_tmpMaxShoulderAngle,_tmpMaxElbowAngle,_tmpAvgHeartRate,_tmpMaxHeartRate,_tmpAvgEmg,_tmpRepetitions,_tmpOverallScore,_tmpPainLevel,_tmpFatigueLevel,_tmpNotes,_tmpIsSynced);
            _result.add(_item);
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
  public Object getUnsyncedSessions(final Continuation<? super List<TrainingSession>> $completion) {
    final String _sql = "SELECT * FROM training_sessions WHERE isSynced = 0";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<TrainingSession>>() {
      @Override
      @NonNull
      public List<TrainingSession> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfStartTime = CursorUtil.getColumnIndexOrThrow(_cursor, "startTime");
          final int _cursorIndexOfEndTime = CursorUtil.getColumnIndexOrThrow(_cursor, "endTime");
          final int _cursorIndexOfDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "duration");
          final int _cursorIndexOfMode = CursorUtil.getColumnIndexOrThrow(_cursor, "mode");
          final int _cursorIndexOfMaxShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxShoulderAngle");
          final int _cursorIndexOfMaxElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "maxElbowAngle");
          final int _cursorIndexOfAvgHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "avgHeartRate");
          final int _cursorIndexOfMaxHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "maxHeartRate");
          final int _cursorIndexOfAvgEmg = CursorUtil.getColumnIndexOrThrow(_cursor, "avgEmg");
          final int _cursorIndexOfRepetitions = CursorUtil.getColumnIndexOrThrow(_cursor, "repetitions");
          final int _cursorIndexOfOverallScore = CursorUtil.getColumnIndexOrThrow(_cursor, "overallScore");
          final int _cursorIndexOfPainLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "painLevel");
          final int _cursorIndexOfFatigueLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "fatigueLevel");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfIsSynced = CursorUtil.getColumnIndexOrThrow(_cursor, "isSynced");
          final List<TrainingSession> _result = new ArrayList<TrainingSession>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingSession _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final long _tmpStartTime;
            _tmpStartTime = _cursor.getLong(_cursorIndexOfStartTime);
            final long _tmpEndTime;
            _tmpEndTime = _cursor.getLong(_cursorIndexOfEndTime);
            final long _tmpDuration;
            _tmpDuration = _cursor.getLong(_cursorIndexOfDuration);
            final String _tmpMode;
            _tmpMode = _cursor.getString(_cursorIndexOfMode);
            final float _tmpMaxShoulderAngle;
            _tmpMaxShoulderAngle = _cursor.getFloat(_cursorIndexOfMaxShoulderAngle);
            final float _tmpMaxElbowAngle;
            _tmpMaxElbowAngle = _cursor.getFloat(_cursorIndexOfMaxElbowAngle);
            final int _tmpAvgHeartRate;
            _tmpAvgHeartRate = _cursor.getInt(_cursorIndexOfAvgHeartRate);
            final int _tmpMaxHeartRate;
            _tmpMaxHeartRate = _cursor.getInt(_cursorIndexOfMaxHeartRate);
            final float _tmpAvgEmg;
            _tmpAvgEmg = _cursor.getFloat(_cursorIndexOfAvgEmg);
            final int _tmpRepetitions;
            _tmpRepetitions = _cursor.getInt(_cursorIndexOfRepetitions);
            final float _tmpOverallScore;
            _tmpOverallScore = _cursor.getFloat(_cursorIndexOfOverallScore);
            final int _tmpPainLevel;
            _tmpPainLevel = _cursor.getInt(_cursorIndexOfPainLevel);
            final int _tmpFatigueLevel;
            _tmpFatigueLevel = _cursor.getInt(_cursorIndexOfFatigueLevel);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final boolean _tmpIsSynced;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSynced);
            _tmpIsSynced = _tmp != 0;
            _item = new TrainingSession(_tmpId,_tmpPatientId,_tmpStartTime,_tmpEndTime,_tmpDuration,_tmpMode,_tmpMaxShoulderAngle,_tmpMaxElbowAngle,_tmpAvgHeartRate,_tmpMaxHeartRate,_tmpAvgEmg,_tmpRepetitions,_tmpOverallScore,_tmpPainLevel,_tmpFatigueLevel,_tmpNotes,_tmpIsSynced);
            _result.add(_item);
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
  public Object getAverageScore(final String patientId,
      final Continuation<? super Float> $completion) {
    final String _sql = "SELECT AVG(overallScore) FROM training_sessions WHERE patientId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
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

  @Override
  public Object getTotalSessionCount(final String patientId,
      final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM training_sessions WHERE patientId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final int _tmp;
            _tmp = _cursor.getInt(0);
            _result = _tmp;
          } else {
            _result = 0;
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
