# User Roles in the System

The system defines the following user roles, each with specific permissions and responsibilities:

## 1. Super Admin
- Has the highest level of access across the system.
- **Permissions**:
  - View, create, update, and delete any user or hospital.
  - Perform all actions without restrictions.

## 2. Hospital Admin
- Manages the operations of a specific hospital.
- **Permissions**:
  - View, create, update, and delete **patients** and **doctors** associated with their hospital only.
  - Update details of their own hospital only.

## 3. Doctor
- Has permissions defined under the **Patient** role with additional functionalities.

## 4. Patient
- Permissions specific to the patient role.
