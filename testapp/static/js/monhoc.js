// static/js/subject.js

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('new-subject-name').addEventListener('keypress', handleAddKeyPress);
    document.getElementById('edit-subject-name').addEventListener('keypress', handleEditKeyPress);
});

// Tìm kiếm
function searchTable() {
    var input = document.getElementById("search-input");
    var filter = input.value.toUpperCase();
    var table = document.getElementById("subject-table");
    var tr = table.getElementsByTagName("tr");
    var hasResult = false;

    for (var i = 1; i < tr.length; i++) {
        tr[i].style.display = "none";
        var td = tr[i].getElementsByTagName("td");
        for (var j = 0; j < td.length; j++) {
            if (td[j]) {
                var txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                    hasResult = true;
                    break;
                }
            }
        }
    }

    document.getElementById("no-results").style.display = filter && !hasResult ? "block" : "none";
    if (!filter) {
        for (var i = 1; i < tr.length; i++) {
            tr[i].style.display = "";
        }
    }
}

function closeAddSubjectModal() {
    document.getElementById("add-subject-modal").style.display = "none";
}

function handleAddKeyPress(event) {
    if (event.key === "Enter") {
        addSubject();
    }
}

function handleEditKeyPress(event) {
    if (event.key === "Enter") {
        saveSubjectEdit();
    }
}

// Thêm môn học
function showAddSubjectModal() {
    Swal.fire({
        title: 'Thêm môn học mới',
        input: 'text',
        inputPlaceholder: 'Nhập tên môn học...',
        showCancelButton: true,
        confirmButtonText: 'Thêm',
        cancelButtonText: 'Hủy',
        inputValidator: (value) => {
            if (!value) {
                return 'Vui lòng nhập tên môn học!';
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            addSubject(result.value);
        }
    });
}

function addSubject(subjectName) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/them_monhoc", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var response = JSON.parse(xhr.responseText);
            if (xhr.status === 200 && response.success) {
                Swal.fire(
                    'Thành công!',
                    'Môn học đã được thêm thành công!',
                    'success'
                ).then(() => location.reload());
            } else {
                if (response.error === "Môn học đã tồn tại!") {
                    Swal.fire(
                        'Lỗi!',
                        'Môn học đã tồn tại trong hệ thống!',
                        'error'
                    );
                } else {
                    Swal.fire(
                        'Lỗi!',
                        response.error || 'Đã xảy ra lỗi khi thêm môn học.',
                        'error'
                    );
                }
            }
        }
    };
    xhr.send(JSON.stringify({ name: subjectName }));
}

// Sửa môn học
function editSubject(id, name) {
    document.getElementById("edit-subject-name").value = name;
    document.getElementById("edit-subject-modal").setAttribute("data-id", id);
    document.getElementById("edit-subject-modal").style.display = "block";
    document.getElementById("edit-subject-name").focus();
    document.getElementById("edit-subject-error").style.display = "none";
}

function closeEditSubjectModal() {
    document.getElementById("edit-subject-modal").style.display = "none";
}

function saveSubjectEdit() {
    var id = document.getElementById("edit-subject-modal").getAttribute("data-id");
    var subjectName = document.getElementById("edit-subject-name").value.trim();
    var errorDiv = document.getElementById("edit-subject-error");

    if (!subjectName) {
        errorDiv.textContent = "Vui lòng nhập tên môn học.";
        errorDiv.style.display = "block";
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("PUT", `/sua_monhoc/${id}`, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var response = JSON.parse(xhr.responseText);
            if (xhr.status === 200 && response.success) {
                Swal.fire(
                    'Thành công!',
                    'Môn học đã được sửa thành công!',
                    'success'
                ).then(() => location.reload());
            } else {
                if (response.error === "Môn học đã tồn tại!") {
                    Swal.fire(
                        'Lỗi!',
                        'Môn học đã tồn tại trong hệ thống!',
                        'error'
                    );
                } else {
                    errorDiv.textContent = response.error || "Đã xảy ra lỗi khi sửa môn học.";
                    errorDiv.style.display = "block";
                }
            }
        }
    };
    xhr.send(JSON.stringify({ name: subjectName }));
}

// Xóa môn học
function deleteSubject(id) {
    Swal.fire({
        title: 'Bạn có chắc chắn muốn xóa?',
        text: "Hành động này không thể hoàn tác!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            var xhr = new XMLHttpRequest();
            xhr.open("DELETE", `/xoa_monhoc/${id}`, true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    Swal.fire(
                        'Đã xóa!',
                        'Môn học đã được xóa thành công.',
                        'success'
                    ).then(() => location.reload());
                }
            };
            xhr.send();
        }
    });
}
