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
import com.rehab.robotarm.data.database.entity.Patient;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Integer;
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
public final class PatientDao_Impl implements PatientDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<Patient> __insertionAdapterOfPatient;

  private final EntityDeletionOrUpdateAdapter<Patient> __deletionAdapterOfPatient;

  private final EntityDeletionOrUpdateAdapter<Patient> __updateAdapterOfPatient;

  private final SharedSQLiteStatement __preparedStmtOfDeactivatePatient;

  public PatientDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfPatient = new EntityInsertionAdapter<Patient>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `patients` (`id`,`name`,`age`,`gender`,`diagnosis`,`affectedSide`,`admissionDate`,`doctorId`,`phoneNumber`,`notes`,`currentROM`,`strengthLevel`,`latestScore`,`isActive`,`createdAt`,`updatedAt`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Patient entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getName());
        statement.bindLong(3, entity.getAge());
        statement.bindString(4, entity.getGender());
        statement.bindString(5, entity.getDiagnosis());
        statement.bindString(6, entity.getAffectedSide());
        statement.bindLong(7, entity.getAdmissionDate());
        statement.bindString(8, entity.getDoctorId());
        statement.bindString(9, entity.getPhoneNumber());
        statement.bindString(10, entity.getNotes());
        statement.bindDouble(11, entity.getCurrentROM());
        statement.bindLong(12, entity.getStrengthLevel());
        statement.bindDouble(13, entity.getLatestScore());
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(14, _tmp);
        statement.bindLong(15, entity.getCreatedAt());
        statement.bindLong(16, entity.getUpdatedAt());
      }
    };
    this.__deletionAdapterOfPatient = new EntityDeletionOrUpdateAdapter<Patient>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `patients` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Patient entity) {
        statement.bindString(1, entity.getId());
      }
    };
    this.__updateAdapterOfPatient = new EntityDeletionOrUpdateAdapter<Patient>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `patients` SET `id` = ?,`name` = ?,`age` = ?,`gender` = ?,`diagnosis` = ?,`affectedSide` = ?,`admissionDate` = ?,`doctorId` = ?,`phoneNumber` = ?,`notes` = ?,`currentROM` = ?,`strengthLevel` = ?,`latestScore` = ?,`isActive` = ?,`createdAt` = ?,`updatedAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Patient entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getName());
        statement.bindLong(3, entity.getAge());
        statement.bindString(4, entity.getGender());
        statement.bindString(5, entity.getDiagnosis());
        statement.bindString(6, entity.getAffectedSide());
        statement.bindLong(7, entity.getAdmissionDate());
        statement.bindString(8, entity.getDoctorId());
        statement.bindString(9, entity.getPhoneNumber());
        statement.bindString(10, entity.getNotes());
        statement.bindDouble(11, entity.getCurrentROM());
        statement.bindLong(12, entity.getStrengthLevel());
        statement.bindDouble(13, entity.getLatestScore());
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(14, _tmp);
        statement.bindLong(15, entity.getCreatedAt());
        statement.bindLong(16, entity.getUpdatedAt());
        statement.bindString(17, entity.getId());
      }
    };
    this.__preparedStmtOfDeactivatePatient = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE patients SET isActive = 0 WHERE id = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insertPatient(final Patient patient, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfPatient.insert(patient);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deletePatient(final Patient patient, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfPatient.handle(patient);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updatePatient(final Patient patient, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfPatient.handle(patient);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deactivatePatient(final String patientId,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeactivatePatient.acquire();
        int _argIndex = 1;
        _stmt.bindString(_argIndex, patientId);
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
          __preparedStmtOfDeactivatePatient.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<Patient>> getAllPatients() {
    final String _sql = "SELECT * FROM patients WHERE isActive = 1 ORDER BY updatedAt DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"patients"}, new Callable<List<Patient>>() {
      @Override
      @NonNull
      public List<Patient> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfAffectedSide = CursorUtil.getColumnIndexOrThrow(_cursor, "affectedSide");
          final int _cursorIndexOfAdmissionDate = CursorUtil.getColumnIndexOrThrow(_cursor, "admissionDate");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfCurrentROM = CursorUtil.getColumnIndexOrThrow(_cursor, "currentROM");
          final int _cursorIndexOfStrengthLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "strengthLevel");
          final int _cursorIndexOfLatestScore = CursorUtil.getColumnIndexOrThrow(_cursor, "latestScore");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<Patient> _result = new ArrayList<Patient>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Patient _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            final String _tmpAffectedSide;
            _tmpAffectedSide = _cursor.getString(_cursorIndexOfAffectedSide);
            final long _tmpAdmissionDate;
            _tmpAdmissionDate = _cursor.getLong(_cursorIndexOfAdmissionDate);
            final String _tmpDoctorId;
            _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final float _tmpCurrentROM;
            _tmpCurrentROM = _cursor.getFloat(_cursorIndexOfCurrentROM);
            final int _tmpStrengthLevel;
            _tmpStrengthLevel = _cursor.getInt(_cursorIndexOfStrengthLevel);
            final float _tmpLatestScore;
            _tmpLatestScore = _cursor.getFloat(_cursorIndexOfLatestScore);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _item = new Patient(_tmpId,_tmpName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpAffectedSide,_tmpAdmissionDate,_tmpDoctorId,_tmpPhoneNumber,_tmpNotes,_tmpCurrentROM,_tmpStrengthLevel,_tmpLatestScore,_tmpIsActive,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getPatientById(final String patientId,
      final Continuation<? super Patient> $completion) {
    final String _sql = "SELECT * FROM patients WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Patient>() {
      @Override
      @Nullable
      public Patient call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfAffectedSide = CursorUtil.getColumnIndexOrThrow(_cursor, "affectedSide");
          final int _cursorIndexOfAdmissionDate = CursorUtil.getColumnIndexOrThrow(_cursor, "admissionDate");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfCurrentROM = CursorUtil.getColumnIndexOrThrow(_cursor, "currentROM");
          final int _cursorIndexOfStrengthLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "strengthLevel");
          final int _cursorIndexOfLatestScore = CursorUtil.getColumnIndexOrThrow(_cursor, "latestScore");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final Patient _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            final String _tmpAffectedSide;
            _tmpAffectedSide = _cursor.getString(_cursorIndexOfAffectedSide);
            final long _tmpAdmissionDate;
            _tmpAdmissionDate = _cursor.getLong(_cursorIndexOfAdmissionDate);
            final String _tmpDoctorId;
            _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final float _tmpCurrentROM;
            _tmpCurrentROM = _cursor.getFloat(_cursorIndexOfCurrentROM);
            final int _tmpStrengthLevel;
            _tmpStrengthLevel = _cursor.getInt(_cursorIndexOfStrengthLevel);
            final float _tmpLatestScore;
            _tmpLatestScore = _cursor.getFloat(_cursorIndexOfLatestScore);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _result = new Patient(_tmpId,_tmpName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpAffectedSide,_tmpAdmissionDate,_tmpDoctorId,_tmpPhoneNumber,_tmpNotes,_tmpCurrentROM,_tmpStrengthLevel,_tmpLatestScore,_tmpIsActive,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<Patient> getPatientByIdFlow(final String patientId) {
    final String _sql = "SELECT * FROM patients WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"patients"}, new Callable<Patient>() {
      @Override
      @Nullable
      public Patient call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfAffectedSide = CursorUtil.getColumnIndexOrThrow(_cursor, "affectedSide");
          final int _cursorIndexOfAdmissionDate = CursorUtil.getColumnIndexOrThrow(_cursor, "admissionDate");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfCurrentROM = CursorUtil.getColumnIndexOrThrow(_cursor, "currentROM");
          final int _cursorIndexOfStrengthLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "strengthLevel");
          final int _cursorIndexOfLatestScore = CursorUtil.getColumnIndexOrThrow(_cursor, "latestScore");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final Patient _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            final String _tmpAffectedSide;
            _tmpAffectedSide = _cursor.getString(_cursorIndexOfAffectedSide);
            final long _tmpAdmissionDate;
            _tmpAdmissionDate = _cursor.getLong(_cursorIndexOfAdmissionDate);
            final String _tmpDoctorId;
            _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final float _tmpCurrentROM;
            _tmpCurrentROM = _cursor.getFloat(_cursorIndexOfCurrentROM);
            final int _tmpStrengthLevel;
            _tmpStrengthLevel = _cursor.getInt(_cursorIndexOfStrengthLevel);
            final float _tmpLatestScore;
            _tmpLatestScore = _cursor.getFloat(_cursorIndexOfLatestScore);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _result = new Patient(_tmpId,_tmpName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpAffectedSide,_tmpAdmissionDate,_tmpDoctorId,_tmpPhoneNumber,_tmpNotes,_tmpCurrentROM,_tmpStrengthLevel,_tmpLatestScore,_tmpIsActive,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<List<Patient>> getPatientsByDoctor(final String doctorId) {
    final String _sql = "SELECT * FROM patients WHERE doctorId = ? AND isActive = 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, doctorId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"patients"}, new Callable<List<Patient>>() {
      @Override
      @NonNull
      public List<Patient> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfAffectedSide = CursorUtil.getColumnIndexOrThrow(_cursor, "affectedSide");
          final int _cursorIndexOfAdmissionDate = CursorUtil.getColumnIndexOrThrow(_cursor, "admissionDate");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfNotes = CursorUtil.getColumnIndexOrThrow(_cursor, "notes");
          final int _cursorIndexOfCurrentROM = CursorUtil.getColumnIndexOrThrow(_cursor, "currentROM");
          final int _cursorIndexOfStrengthLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "strengthLevel");
          final int _cursorIndexOfLatestScore = CursorUtil.getColumnIndexOrThrow(_cursor, "latestScore");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<Patient> _result = new ArrayList<Patient>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Patient _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            final String _tmpAffectedSide;
            _tmpAffectedSide = _cursor.getString(_cursorIndexOfAffectedSide);
            final long _tmpAdmissionDate;
            _tmpAdmissionDate = _cursor.getLong(_cursorIndexOfAdmissionDate);
            final String _tmpDoctorId;
            _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final String _tmpNotes;
            _tmpNotes = _cursor.getString(_cursorIndexOfNotes);
            final float _tmpCurrentROM;
            _tmpCurrentROM = _cursor.getFloat(_cursorIndexOfCurrentROM);
            final int _tmpStrengthLevel;
            _tmpStrengthLevel = _cursor.getInt(_cursorIndexOfStrengthLevel);
            final float _tmpLatestScore;
            _tmpLatestScore = _cursor.getFloat(_cursorIndexOfLatestScore);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final long _tmpUpdatedAt;
            _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            _item = new Patient(_tmpId,_tmpName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpAffectedSide,_tmpAdmissionDate,_tmpDoctorId,_tmpPhoneNumber,_tmpNotes,_tmpCurrentROM,_tmpStrengthLevel,_tmpLatestScore,_tmpIsActive,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getActivePatientCount(final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM patients WHERE isActive = 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
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
