import { Component, OnInit, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { UploadedFiles, UploadedFile, UploadFile_Permission } from '../../models/models';
import { FileUpload } from 'primeng/fileupload';
import { environment } from '../../../environments/environment';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-file-maintainer',
  templateUrl: './file-maintainer.component.html',
  styleUrls: ['./file-maintainer.component.css']
})
export class FileMaintainerComponent implements OnInit {

  @ViewChild('reqUploader', { static: false }) reqUploader: FileUpload;

  private _uploaded_files: UploadedFiles;
  private _origin_uploaded_files: UploadedFiles;
  @Input() set uploaded_files(files: UploadedFiles) {
    this._uploaded_files = files;
    this._origin_uploaded_files = (files) ? JSON.parse(JSON.stringify(files)) : {};
  }
  get uploaded_files(): UploadedFiles {
    return this._uploaded_files;
  }
  @Input() uploadfile_permissions: UploadFile_Permission[];
  @Input() editable: boolean;

  delete_files: Map<number, any> = new Map();

  files_for_upload: any[] = [];
  @Output() deletedFiles = new EventEmitter<number[]>();
  @Output() updatedSomething = new EventEmitter<boolean>();
  upload_req_status: number;

  constructor(private cookieService: CookieService) { }

  ngOnInit() {
  }

  toggleDeleteFile(file: UploadedFile) {
    if (file['deleted']) {
      this.delete_files.delete(file.id);
      file['deleted'] = false;
    } else {
      this.delete_files.set(file.id, null);
      file['deleted'] = true;
    }
    let rtn_arr: number[] = Array.from(this.delete_files.keys());
    this.deletedFiles.emit(rtn_arr);
    this.updatedSomethingOnScreen();
  }

  updatedSomethingOnScreen() {
    this.updatedSomething.emit(true);
  }
  uploadFiles(request_id: number, status?: number) {
    const baseurl = environment.baseUrl;
    this.reqUploader.url = `${baseurl}/upload/request/${request_id}/`;
    this.upload_req_status = status;
    this.reqUploader.upload();
  }
  onBeforeSend(event: any) {
    if (event && event.xhr) {
      event.xhr.setRequestHeader('X-CSRFToken', this.cookieService.get('csrftoken'));
    }
  }
  onBeforeUpload(event: any) {
    if (typeof this.upload_req_status !== 'undefined') {
      let formData = event.formData;
      formData.append('status', this.upload_req_status);
    }
  }

  clearUpload() {
    if (this.reqUploader) {
      this.reqUploader.clear();
    }
    this.uploaded_files = JSON.parse(JSON.stringify(this._origin_uploaded_files));
  }
}
