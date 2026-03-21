package com.rehab.robotarm.data.database.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.rehab.robotarm.data.database.entity.SensorRecord;
import java.lang.Class;
import java.lang.Exception;
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
public final class SensorRecordDao_Impl implements SensorRecordDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<SensorRecord> __insertionAdapterOfSensorRecord;

  private final SharedSQLiteStatement __preparedStmtOfDeleteBySession;

  private final SharedSQLiteStatement __preparedStmtOfDeleteOldRecords;

  public SensorRecordDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfSensorRecord = new EntityInsertionAdapter<SensorRecord>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `sensor_records` (`id`,`sessionId`,`timestamp`,`shoulderAngle`,`elbowAngle`,`wristAngle`,`lateralPosition`,`shoulderTorque`,`elbowTorque`,`wristTorque`,`shoulderForce`,`elbowForce`,`emgCh1`,`emgCh2`,`imuAccelX`,`imuAccelY`,`imuAccelZ`,`imuGyroX`,`imuGyroY`,`imuGyroZ`,`heartRate`,`spo2`,`shoulderTemp`,`elbowTemp`,`lateralTemp`) VALUES (nullif(?, 0),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final SensorRecord entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getSessionId());
        statement.bindLong(3, entity.getTimestamp());
        statement.bindDouble(4, entity.getShoulderAngle());
        statement.bindDouble(5, entity.getElbowAngle());
        statement.bindDouble(6, entity.getWristAngle());
        statement.bindDouble(7, entity.getLateralPosition());
        statement.bindDouble(8, entity.getShoulderTorque());
        statement.bindDouble(9, entity.getElbowTorque());
        statement.bindDouble(10, entity.getWristTorque());
        statement.bindDouble(11, entity.getShoulderForce());
        statement.bindDouble(12, entity.getElbowForce());
        statement.bindDouble(13, entity.getEmgCh1());
        statement.bindDouble(14, entity.getEmgCh2());
        statement.bindDouble(15, entity.getImuAccelX());
        statement.bindDouble(16, entity.getImuAccelY());
        statement.bindDouble(17, entity.getImuAccelZ());
        statement.bindDouble(18, entity.getImuGyroX());
        statement.bindDouble(19, entity.getImuGyroY());
        statement.bindDouble(20, entity.getImuGyroZ());
        statement.bindLong(21, entity.getHeartRate());
        statement.bindLong(22, entity.getSpo2());
        statement.bindDouble(23, entity.getShoulderTemp());
        statement.bindDouble(24, entity.getElbowTemp());
        statement.bindDouble(25, entity.getLateralTemp());
      }
    };
    this.__preparedStmtOfDeleteBySession = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM sensor_records WHERE sessionId = ?";
        return _query;
      }
    };
    this.__preparedStmtOfDeleteOldRecords = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM sensor_records WHERE timestamp < ?";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final SensorRecord record, final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfSensorRecord.insertAndReturnId(record);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertAll(final List<SensorRecord> records,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfSensorRecord.insert(records);
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
  public Object deleteOldRecords(final long timestamp,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteOldRecords.acquire();
        int _argIndex = 1;
        _stmt.bindLong(_argIndex, timestamp);
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
          __preparedStmtOfDeleteOldRecords.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<SensorRecord>> getRecordsBySession(final String sessionId) {
    final String _sql = "SELECT * FROM sensor_records WHERE sessionId = ? ORDER BY timestamp ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"sensor_records"}, new Callable<List<SensorRecord>>() {
      @Override
      @NonNull
      public List<SensorRecord> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderAngle");
          final int _cursorIndexOfElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowAngle");
          final int _cursorIndexOfWristAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "wristAngle");
          final int _cursorIndexOfLateralPosition = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralPosition");
          final int _cursorIndexOfShoulderTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTorque");
          final int _cursorIndexOfElbowTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTorque");
          final int _cursorIndexOfWristTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "wristTorque");
          final int _cursorIndexOfShoulderForce = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderForce");
          final int _cursorIndexOfElbowForce = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowForce");
          final int _cursorIndexOfEmgCh1 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh1");
          final int _cursorIndexOfEmgCh2 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh2");
          final int _cursorIndexOfImuAccelX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelX");
          final int _cursorIndexOfImuAccelY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelY");
          final int _cursorIndexOfImuAccelZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelZ");
          final int _cursorIndexOfImuGyroX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroX");
          final int _cursorIndexOfImuGyroY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroY");
          final int _cursorIndexOfImuGyroZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroZ");
          final int _cursorIndexOfHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "heartRate");
          final int _cursorIndexOfSpo2 = CursorUtil.getColumnIndexOrThrow(_cursor, "spo2");
          final int _cursorIndexOfShoulderTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTemp");
          final int _cursorIndexOfElbowTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTemp");
          final int _cursorIndexOfLateralTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralTemp");
          final List<SensorRecord> _result = new ArrayList<SensorRecord>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final SensorRecord _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
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
            final float _tmpLateralPosition;
            _tmpLateralPosition = _cursor.getFloat(_cursorIndexOfLateralPosition);
            final float _tmpShoulderTorque;
            _tmpShoulderTorque = _cursor.getFloat(_cursorIndexOfShoulderTorque);
            final float _tmpElbowTorque;
            _tmpElbowTorque = _cursor.getFloat(_cursorIndexOfElbowTorque);
            final float _tmpWristTorque;
            _tmpWristTorque = _cursor.getFloat(_cursorIndexOfWristTorque);
            final float _tmpShoulderForce;
            _tmpShoulderForce = _cursor.getFloat(_cursorIndexOfShoulderForce);
            final float _tmpElbowForce;
            _tmpElbowForce = _cursor.getFloat(_cursorIndexOfElbowForce);
            final float _tmpEmgCh1;
            _tmpEmgCh1 = _cursor.getFloat(_cursorIndexOfEmgCh1);
            final float _tmpEmgCh2;
            _tmpEmgCh2 = _cursor.getFloat(_cursorIndexOfEmgCh2);
            final float _tmpImuAccelX;
            _tmpImuAccelX = _cursor.getFloat(_cursorIndexOfImuAccelX);
            final float _tmpImuAccelY;
            _tmpImuAccelY = _cursor.getFloat(_cursorIndexOfImuAccelY);
            final float _tmpImuAccelZ;
            _tmpImuAccelZ = _cursor.getFloat(_cursorIndexOfImuAccelZ);
            final float _tmpImuGyroX;
            _tmpImuGyroX = _cursor.getFloat(_cursorIndexOfImuGyroX);
            final float _tmpImuGyroY;
            _tmpImuGyroY = _cursor.getFloat(_cursorIndexOfImuGyroY);
            final float _tmpImuGyroZ;
            _tmpImuGyroZ = _cursor.getFloat(_cursorIndexOfImuGyroZ);
            final int _tmpHeartRate;
            _tmpHeartRate = _cursor.getInt(_cursorIndexOfHeartRate);
            final int _tmpSpo2;
            _tmpSpo2 = _cursor.getInt(_cursorIndexOfSpo2);
            final float _tmpShoulderTemp;
            _tmpShoulderTemp = _cursor.getFloat(_cursorIndexOfShoulderTemp);
            final float _tmpElbowTemp;
            _tmpElbowTemp = _cursor.getFloat(_cursorIndexOfElbowTemp);
            final float _tmpLateralTemp;
            _tmpLateralTemp = _cursor.getFloat(_cursorIndexOfLateralTemp);
            _item = new SensorRecord(_tmpId,_tmpSessionId,_tmpTimestamp,_tmpShoulderAngle,_tmpElbowAngle,_tmpWristAngle,_tmpLateralPosition,_tmpShoulderTorque,_tmpElbowTorque,_tmpWristTorque,_tmpShoulderForce,_tmpElbowForce,_tmpEmgCh1,_tmpEmgCh2,_tmpImuAccelX,_tmpImuAccelY,_tmpImuAccelZ,_tmpImuGyroX,_tmpImuGyroY,_tmpImuGyroZ,_tmpHeartRate,_tmpSpo2,_tmpShoulderTemp,_tmpElbowTemp,_tmpLateralTemp);
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
  public Object getRecordsBySessionSync(final String sessionId,
      final Continuation<? super List<SensorRecord>> $completion) {
    final String _sql = "SELECT * FROM sensor_records WHERE sessionId = ? ORDER BY timestamp ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<SensorRecord>>() {
      @Override
      @NonNull
      public List<SensorRecord> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderAngle");
          final int _cursorIndexOfElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowAngle");
          final int _cursorIndexOfWristAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "wristAngle");
          final int _cursorIndexOfLateralPosition = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralPosition");
          final int _cursorIndexOfShoulderTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTorque");
          final int _cursorIndexOfElbowTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTorque");
          final int _cursorIndexOfWristTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "wristTorque");
          final int _cursorIndexOfShoulderForce = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderForce");
          final int _cursorIndexOfElbowForce = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowForce");
          final int _cursorIndexOfEmgCh1 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh1");
          final int _cursorIndexOfEmgCh2 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh2");
          final int _cursorIndexOfImuAccelX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelX");
          final int _cursorIndexOfImuAccelY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelY");
          final int _cursorIndexOfImuAccelZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelZ");
          final int _cursorIndexOfImuGyroX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroX");
          final int _cursorIndexOfImuGyroY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroY");
          final int _cursorIndexOfImuGyroZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroZ");
          final int _cursorIndexOfHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "heartRate");
          final int _cursorIndexOfSpo2 = CursorUtil.getColumnIndexOrThrow(_cursor, "spo2");
          final int _cursorIndexOfShoulderTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTemp");
          final int _cursorIndexOfElbowTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTemp");
          final int _cursorIndexOfLateralTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralTemp");
          final List<SensorRecord> _result = new ArrayList<SensorRecord>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final SensorRecord _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
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
            final float _tmpLateralPosition;
            _tmpLateralPosition = _cursor.getFloat(_cursorIndexOfLateralPosition);
            final float _tmpShoulderTorque;
            _tmpShoulderTorque = _cursor.getFloat(_cursorIndexOfShoulderTorque);
            final float _tmpElbowTorque;
            _tmpElbowTorque = _cursor.getFloat(_cursorIndexOfElbowTorque);
            final float _tmpWristTorque;
            _tmpWristTorque = _cursor.getFloat(_cursorIndexOfWristTorque);
            final float _tmpShoulderForce;
            _tmpShoulderForce = _cursor.getFloat(_cursorIndexOfShoulderForce);
            final float _tmpElbowForce;
            _tmpElbowForce = _cursor.getFloat(_cursorIndexOfElbowForce);
            final float _tmpEmgCh1;
            _tmpEmgCh1 = _cursor.getFloat(_cursorIndexOfEmgCh1);
            final float _tmpEmgCh2;
            _tmpEmgCh2 = _cursor.getFloat(_cursorIndexOfEmgCh2);
            final float _tmpImuAccelX;
            _tmpImuAccelX = _cursor.getFloat(_cursorIndexOfImuAccelX);
            final float _tmpImuAccelY;
            _tmpImuAccelY = _cursor.getFloat(_cursorIndexOfImuAccelY);
            final float _tmpImuAccelZ;
            _tmpImuAccelZ = _cursor.getFloat(_cursorIndexOfImuAccelZ);
            final float _tmpImuGyroX;
            _tmpImuGyroX = _cursor.getFloat(_cursorIndexOfImuGyroX);
            final float _tmpImuGyroY;
            _tmpImuGyroY = _cursor.getFloat(_cursorIndexOfImuGyroY);
            final float _tmpImuGyroZ;
            _tmpImuGyroZ = _cursor.getFloat(_cursorIndexOfImuGyroZ);
            final int _tmpHeartRate;
            _tmpHeartRate = _cursor.getInt(_cursorIndexOfHeartRate);
            final int _tmpSpo2;
            _tmpSpo2 = _cursor.getInt(_cursorIndexOfSpo2);
            final float _tmpShoulderTemp;
            _tmpShoulderTemp = _cursor.getFloat(_cursorIndexOfShoulderTemp);
            final float _tmpElbowTemp;
            _tmpElbowTemp = _cursor.getFloat(_cursorIndexOfElbowTemp);
            final float _tmpLateralTemp;
            _tmpLateralTemp = _cursor.getFloat(_cursorIndexOfLateralTemp);
            _item = new SensorRecord(_tmpId,_tmpSessionId,_tmpTimestamp,_tmpShoulderAngle,_tmpElbowAngle,_tmpWristAngle,_tmpLateralPosition,_tmpShoulderTorque,_tmpElbowTorque,_tmpWristTorque,_tmpShoulderForce,_tmpElbowForce,_tmpEmgCh1,_tmpEmgCh2,_tmpImuAccelX,_tmpImuAccelY,_tmpImuAccelZ,_tmpImuGyroX,_tmpImuGyroY,_tmpImuGyroZ,_tmpHeartRate,_tmpSpo2,_tmpShoulderTemp,_tmpElbowTemp,_tmpLateralTemp);
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
  public Object getRecentRecords(final String sessionId, final int limit,
      final Continuation<? super List<SensorRecord>> $completion) {
    final String _sql = "SELECT * FROM sensor_records WHERE sessionId = ? ORDER BY timestamp DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 2);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
    _argIndex = 2;
    _statement.bindLong(_argIndex, limit);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<SensorRecord>>() {
      @Override
      @NonNull
      public List<SensorRecord> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSessionId = CursorUtil.getColumnIndexOrThrow(_cursor, "sessionId");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfShoulderAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderAngle");
          final int _cursorIndexOfElbowAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowAngle");
          final int _cursorIndexOfWristAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "wristAngle");
          final int _cursorIndexOfLateralPosition = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralPosition");
          final int _cursorIndexOfShoulderTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTorque");
          final int _cursorIndexOfElbowTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTorque");
          final int _cursorIndexOfWristTorque = CursorUtil.getColumnIndexOrThrow(_cursor, "wristTorque");
          final int _cursorIndexOfShoulderForce = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderForce");
          final int _cursorIndexOfElbowForce = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowForce");
          final int _cursorIndexOfEmgCh1 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh1");
          final int _cursorIndexOfEmgCh2 = CursorUtil.getColumnIndexOrThrow(_cursor, "emgCh2");
          final int _cursorIndexOfImuAccelX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelX");
          final int _cursorIndexOfImuAccelY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelY");
          final int _cursorIndexOfImuAccelZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuAccelZ");
          final int _cursorIndexOfImuGyroX = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroX");
          final int _cursorIndexOfImuGyroY = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroY");
          final int _cursorIndexOfImuGyroZ = CursorUtil.getColumnIndexOrThrow(_cursor, "imuGyroZ");
          final int _cursorIndexOfHeartRate = CursorUtil.getColumnIndexOrThrow(_cursor, "heartRate");
          final int _cursorIndexOfSpo2 = CursorUtil.getColumnIndexOrThrow(_cursor, "spo2");
          final int _cursorIndexOfShoulderTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "shoulderTemp");
          final int _cursorIndexOfElbowTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "elbowTemp");
          final int _cursorIndexOfLateralTemp = CursorUtil.getColumnIndexOrThrow(_cursor, "lateralTemp");
          final List<SensorRecord> _result = new ArrayList<SensorRecord>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final SensorRecord _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
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
            final float _tmpLateralPosition;
            _tmpLateralPosition = _cursor.getFloat(_cursorIndexOfLateralPosition);
            final float _tmpShoulderTorque;
            _tmpShoulderTorque = _cursor.getFloat(_cursorIndexOfShoulderTorque);
            final float _tmpElbowTorque;
            _tmpElbowTorque = _cursor.getFloat(_cursorIndexOfElbowTorque);
            final float _tmpWristTorque;
            _tmpWristTorque = _cursor.getFloat(_cursorIndexOfWristTorque);
            final float _tmpShoulderForce;
            _tmpShoulderForce = _cursor.getFloat(_cursorIndexOfShoulderForce);
            final float _tmpElbowForce;
            _tmpElbowForce = _cursor.getFloat(_cursorIndexOfElbowForce);
            final float _tmpEmgCh1;
            _tmpEmgCh1 = _cursor.getFloat(_cursorIndexOfEmgCh1);
            final float _tmpEmgCh2;
            _tmpEmgCh2 = _cursor.getFloat(_cursorIndexOfEmgCh2);
            final float _tmpImuAccelX;
            _tmpImuAccelX = _cursor.getFloat(_cursorIndexOfImuAccelX);
            final float _tmpImuAccelY;
            _tmpImuAccelY = _cursor.getFloat(_cursorIndexOfImuAccelY);
            final float _tmpImuAccelZ;
            _tmpImuAccelZ = _cursor.getFloat(_cursorIndexOfImuAccelZ);
            final float _tmpImuGyroX;
            _tmpImuGyroX = _cursor.getFloat(_cursorIndexOfImuGyroX);
            final float _tmpImuGyroY;
            _tmpImuGyroY = _cursor.getFloat(_cursorIndexOfImuGyroY);
            final float _tmpImuGyroZ;
            _tmpImuGyroZ = _cursor.getFloat(_cursorIndexOfImuGyroZ);
            final int _tmpHeartRate;
            _tmpHeartRate = _cursor.getInt(_cursorIndexOfHeartRate);
            final int _tmpSpo2;
            _tmpSpo2 = _cursor.getInt(_cursorIndexOfSpo2);
            final float _tmpShoulderTemp;
            _tmpShoulderTemp = _cursor.getFloat(_cursorIndexOfShoulderTemp);
            final float _tmpElbowTemp;
            _tmpElbowTemp = _cursor.getFloat(_cursorIndexOfElbowTemp);
            final float _tmpLateralTemp;
            _tmpLateralTemp = _cursor.getFloat(_cursorIndexOfLateralTemp);
            _item = new SensorRecord(_tmpId,_tmpSessionId,_tmpTimestamp,_tmpShoulderAngle,_tmpElbowAngle,_tmpWristAngle,_tmpLateralPosition,_tmpShoulderTorque,_tmpElbowTorque,_tmpWristTorque,_tmpShoulderForce,_tmpElbowForce,_tmpEmgCh1,_tmpEmgCh2,_tmpImuAccelX,_tmpImuAccelY,_tmpImuAccelZ,_tmpImuGyroX,_tmpImuGyroY,_tmpImuGyroZ,_tmpHeartRate,_tmpSpo2,_tmpShoulderTemp,_tmpElbowTemp,_tmpLateralTemp);
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
  public Object getRecordCount(final String sessionId,
      final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM sensor_records WHERE sessionId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, sessionId);
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
