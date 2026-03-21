package com.rehab.robotarm.data.database.dao;

import android.database.Cursor;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.rehab.robotarm.data.database.entity.TrainingRecord;
import java.lang.Class;
import java.lang.Exception;
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
public final class TrainingRecordDao_Impl implements TrainingRecordDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TrainingRecord> __insertionAdapterOfTrainingRecord;

  private final SharedSQLiteStatement __preparedStmtOfDeleteRecordsBySession;

  public TrainingRecordDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTrainingRecord = new EntityInsertionAdapter<TrainingRecord>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `training_records` (`id`,`sessionId`,`timestamp`,`shoulderAngle`,`elbowAngle`,`wristAngle`,`emgCh1`,`emgCh2`,`heartRate`,`spo2`,`torqueX`,`torqueY`,`torqueZ`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingRecord entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getSessionId());
        statement.bindLong(3, entity.getTimestamp());
        statement.bindDouble(4, entity.getShoulderAngle());
        statement.bindDouble(5, entity.getElbowAngle());
        statement.bindDouble(6, entity.getWristAngle());
        statement.bindDouble(7, entity.getEmgCh1());
        statement.bindDouble(8, entity.getEmgCh2());
        statement.bindLong(9, entity.getHeartRate());
        statement.bindLong(10, entity.getSpo2());
        statement.bindDouble(11, entity.getTorqueX());
        statement.bindDouble(12, entity.getTorqueY());
        statement.bindDouble(13, entity.getTorqueZ());
      }
    };
    this.__preparedStmtOfDeleteRecordsBySession = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM training_records WHERE sessionId = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insertRecord(final TrainingRecord record,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrainingRecord.insert(record);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertRecords(final List<TrainingRecord> records,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrainingRecord.insert(records);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteRecordsBySession(final String sessionId,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteRecordsBySession.acquire();
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
          __preparedStmtOfDeleteRecordsBySession.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<TrainingRecord>> getRecordsBySession(final String sessionId) {
    final String _sql = "SELECT * FROM training_records WHERE sessionId = ? ORDER BY timestamp ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"training_records"}, new Callable<List<TrainingRecord>>() {
      @Override
      @NonNull
      public List<TrainingRecord> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderAngle");
          final int _cursorIndexOfElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowAngle");
          final int _cursorIndexOfWristAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "wristAngle");
          final int _cursorIndexOfEmgCh1 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh1");
          final int _cursorIndexOfEmgCh2 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh2");
          final int _cursorIndexOfHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "heartRate");
          final int _cursorIndexOfSpo2 = CursorUtil.getColumnIndexOrThrow(_cursor, "spo2");
          final int _cursorIndexOfTorqueX = CursorUtil.getColumnIndexOrThrow(_cursor, "torqueX");
          final int _cursorIndexOfTorqueY = CursorUtil.getColumnIndexOrThrow(_cursor, "torqueY");
          final int _cursorIndexOfTorqueZ = CursorUtil.getColumnIndexOrThrow(_cursor, "torqueZ");
          final List<TrainingRecord> _result = new ArrayList<TrainingRecord>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final TrainingRecord _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpSessionId;
            _tmpSessionId = _cursor.getString(_cursorIndexOfSessionId);
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final float _tmpShoulderAngle;
            _tmpShoulderAngle = _cursor.getFloat(_cursorIndexOfShoulderAngle);
            final float _tmpElbowAngle;
            _tmpElbowAngle = _cursor.getFloat(_cursorIndexOfElbowAngle);
            final float _tmpWristAngle;
            _tmpWristAngle = _cursor.getFloat(_cursorIndexOfWristAngle);
            final float _tmpEmgCh1;
            _tmpEmgCh1 = _cursor.getFloat(_cursorIndexOfEmgCh1);
            final float _tmpEmgCh2;
            _tmpEmgCh2 = _cursor.getFloat(_cursorIndexOfEmgCh2);
            final int _tmpHeartRate;
            _tmpHeartRate = _cursor.getInt(_cursorIndexOfHeartRate);
            final int _tmpSpo2;
            _tmpSpo2 = _cursor.getInt(_cursorIndexOfSpo2);
            final float _tmpTorqueX;
            _tmpTorqueX = _cursor.getFloat(_cursorIndexOfTorqueX);
            final float _tmpTorqueY;
            _tmpTorqueY = _cursor.getFloat(_cursorIndexOfTorqueY);
            final float _tmpTorqueZ;
            _tmpTorqueZ = _cursor.getFloat(_cursorIndexOfTorqueZ);
            _item = new TrainingRecord(_tmpId,_tmpSessionId,_tmpTimestamp,_tmpShoulderAngle,_tmpElbowAngle,_tmpWristAngle,_tmpEmgCh1,_tmpEmgCh2,_tmpHeartRate,_tmpSpo2,_tmpTorqueX,_tmpTorqueY,_tmpTorqueZ);
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

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
