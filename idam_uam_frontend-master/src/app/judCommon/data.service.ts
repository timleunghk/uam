import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { GenericAccountRequest, BaseRequest, GenericAccountReview, GenericAccountExecute, MailAddr, LoginUserInfo, Section, AdGroup, LnGroup, Rank, AdOU, AdName, SimpleCode, RomaInfo } from '../models/models'
import { formatDate } from '@angular/common';
import { AppConfigService } from './config-service'
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})

export class DataService {
  API_URL = environment.baseUrl;
  date_format = "dd/MM/yyyy"
  date_format_full = "dd/MM/yyyy HH:mm:ss"

  current_user: LoginUserInfo;

  hasPermission(permissions: string[]) {
    if (this.current_user) {
      for (let permission of permissions) {
        if (this.current_user.permissions.includes(permission)) {
          return true;
        }
      }
    }
    return false;
  }

  canSelectSection(): boolean {
    if (this.hasPermission(['uam_requests.can_manage_all_sections'])) {
      return true;
    }
    return false;
  }
  constructor(private http: HttpClient, private appConfigService: AppConfigService) {
  }

  private transformUpdateFKField(body: any, field: string) {
    // move field to an update field for Background ForeignKeyPersonalInfoMixin to consume
    // e.g. section -> updated_section, master_rank -> updated_master_rank
    if (field in body) {
      let obj = body[field];
      delete body[field];
      if (obj != null && obj !== undefined) {
        body[`updated_${field}`] = obj;
      } else {
        body[`updated_${field}`] = null;
      }
    }
  }

  private cloneRequestForRemoteCall(request: GenericAccountRequest) {
    let body = JSON.parse(JSON.stringify(request));
    body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;
    // body.ad_account_expiry_date = request['ad_account_expiry_date'] ? formatDate(request['ad_account_expiry_date'], this.date_format, 'en') : null;
    if (request['ad_account_expiry_date']) {
      body.ad_account_expiry_date = (typeof request['ad_account_expiry_date'] === 'string') ? request['ad_account_expiry_date'] : formatDate(request['ad_account_expiry_date'], this.date_format, 'en');
    } else {
      body.ad_account_expiry_date = null;  
    }
    this.transformUpdateFKField(body, 'section');
    this.transformUpdateFKField(body, 'master_rank');
    this.transformUpdateFKField(body, 'substantive_rank');
    return body;
  }
  getCreateAccountPrepare(request_id: string = null) {

    let tmpstr = ''
    if (request_id != null) {
      tmpstr = `?request_id=${request_id}`
    }
    return this.http.get<GenericAccountRequest[]>(`${this.API_URL}/create_account_requests/prepare/${tmpstr}`);
    // .toPromise().then(res => <GenericAccountRequest[]> res.data)
    // .then(data => { return data; });
  }

  updateCreateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);

    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    if (tmp_id) {
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/create_account_requests/prepare/${tmp_id}/draft/`, body);
    } else {
      return this.http.post<GenericAccountRequest>(`${this.API_URL}/create_account_requests/prepare/draft/`, body);
    }
  }

  submitCreateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    if (tmp_id) {
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/create_account_requests/prepare/${tmp_id}/`, body);
    } else {
      return this.http.post<GenericAccountRequest>(`${this.API_URL}/create_account_requests/prepare/`, body);
    }
  }

  withdrawCreateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    if (tmp_id) {
      let body = this.cloneRequestForRemoteCall(request);
      // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
      // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/create_account_requests/prepare/${tmp_id}/reject/`, body);
    }
  }
  updateCreateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);

    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/create_account_requests/review/${tmp_id}/draft/`, body);
  }

  endorseCreateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/create_account_requests/review/${tmp_id}/`, body);
  }

  rejectCreateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/create_account_requests/review/${tmp_id}/reject/`, body);
  }

  rejectUpdateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/update_account_requests/review/${tmp_id}/reject/`, body);
  }

  updateCreateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/create_account_requests/execute/${tmp_id}/draft/`, body);
  }

  completeCreateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/create_account_requests/execute/${tmp_id}/`, body);
  }

  rejectCreateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/create_account_requests/execute/${tmp_id}/reject/`, body);
  }

  getAllRequests(searchData: any) {
    let params = new HttpParams();
    for (let key in searchData) {
      if (searchData[key] !== null && searchData[key] !== '' && typeof searchData[key] !== 'undefined') {
        params = params.set(key, searchData[key]);
      }
    }
    // console.log(params);
    return this.http.get<BaseRequest[]>(`${this.API_URL}/requests/`, { params });
    // return this.http.post<BaseRequest[]>(`${this.API_URL}/requests/`, searchData);
  }

  getAllRequestsAsync(searchData: any) {
    return this.http.post<BaseRequest[]>(`${this.API_URL}/requests/`, searchData).toPromise();
  }

  // getAllToDoListRequests(searchData: any) {
  //   return this.http.post<BaseRequest[]>(`${this.API_URL}/requests_todolist/`, searchData);
  // }

  getRequest(id: number) {
    return this.http.get<BaseRequest>(`${this.API_URL}/requests/${id}/`);
  }

  getRequestAsync(id: number) {
    return this.http.get<BaseRequest>(`${this.API_URL}/requests/${id}/`).toPromise();
  }

  getRequestAuditlog(request_id: string) {
    return this.http.get(`${this.API_URL}/audit_log/request/${request_id}/`);
  }

  getUserAccounts(searchData: any, for_update: boolean = false) {
    let params = new HttpParams();
    for (let key in searchData) {
      if (searchData[key] !== null && searchData[key] !== '' && typeof searchData[key] !== 'undefined') {
        params = params.set(key, searchData[key]);
      }
    }
    if (for_update) {
      params = params.set('for_update', '1')
    }
    // console.log(params);
    return this.http.get<any[]>(`${this.API_URL}/users_account/`, { params });
  }

  // getAllUserAccounts(searchData: any) {
  //   return this.http.post<any[]>(`${this.API_URL}/users_account/`, searchData);
  // }

  disableUserAccounts(ids: any) {
    return this.http.post<any>(`${this.API_URL}/users_account_disable/`, ids);
  }

  enbleUserAccounts(ids: any) {
    return this.http.post<any>(`${this.API_URL}/users_account_enable/`, ids);
  }

  deleteUserAccounts(ids: any) {
    return this.http.post<any>(`${this.API_URL}/users_account_delete/`, ids);
  }

  getUser(id: number, for_update: boolean = false) {
    if (for_update) {
      const params = new HttpParams().set('for_update', '1');
      return this.http.get<BaseRequest>(`${this.API_URL}/users_account/${id}/`, { params });
    } else {
      return this.http.get<BaseRequest>(`${this.API_URL}/users_account/${id}/`);
    }
  }

  chgPwd(ids: any) {
    return this.http.post<any>(`${this.API_URL}/reset_pwd_requests/`, ids);
  }

  setupComplete(id: any) {
    return this.http.put<any>(`${this.API_URL}/create_account_requests/setupcomp/${id}/`, {})
  }

  userAck(id: any) {
    return this.http.put<any>(`${this.API_URL}/create_account_requests/userack/${id}/`, {})
  }

  getPersonal(id: any) {
    return this.http.get<any>(`${this.API_URL}/users_account/${id}/`);
  }

  saveUpdateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    if (tmp_id) {
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/update_account_requests/prepare/${tmp_id}/draft/`, body);
    } else {
      return this.http.post<GenericAccountRequest>(`${this.API_URL}/update_account_requests/prepare/draft/`, body);
    }
  }

  submitUpdateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    if (tmp_id) {
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/update_account_requests/prepare/${tmp_id}/`, body);
    } else {
      return this.http.post<GenericAccountRequest>(`${this.API_URL}/update_account_requests/prepare/`, body);
    }
  }


  withdrawUpdateAccountPrepare(request: GenericAccountRequest) {
    let tmp_id: number = request.id;
    if (tmp_id) {
      let body = this.cloneRequestForRemoteCall(request);
      // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
      // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;
      return this.http.put<GenericAccountRequest>(`${this.API_URL}/update_account_requests/prepare/${tmp_id}/reject/`, body);
    }

  }
  saveUpdateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/update_account_requests/review/${tmp_id}/draft/`, body);
  }

  endorseUpdateAccountReview(request: GenericAccountReview) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountReview>(`${this.API_URL}/update_account_requests/review/${tmp_id}/`, body);
  }

  completeUpdateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/update_account_requests/execute/${tmp_id}/`, body);
  }

  rejectUpdateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/update_account_requests/execute/${tmp_id}/reject/`, body);
  }

  saveUpdateAccountExecute(request: GenericAccountExecute) {
    let tmp_id: number = request.id;
    let body = this.cloneRequestForRemoteCall(request);
    // body.account_effective_start_date = request.account_effective_start_date ? formatDate(request.account_effective_start_date, this.date_format, 'en') : null;
    // body.account_effective_end_date = request.account_effective_end_date ? formatDate(request.account_effective_end_date, this.date_format, 'en') : null;

    return this.http.put<GenericAccountExecute>(`${this.API_URL}/update_account_requests/execute/${tmp_id}/draft/`, body);
  }

  // getDP(romaID: string) {
  //   return { dp_hkid: 'A123456', dp_full_name: "CHAN , Tai Man" };
  // }

  searchMail(mailSearch: string) {
    const params = new HttpParams().set('mail_name', mailSearch);
    return this.http.get<MailAddr[]>(`${this.API_URL}/mailaddrs/`, { params });
  }

  getPS(name: string) {
    const params = new HttpParams().set('name', name);
    return this.http.get<AdName[]>(`${this.API_URL}/adnames/`, { params });
  }

  getCurrentUserInfo() {
    return this.http.get<LoginUserInfo>(`${this.API_URL}/auth/user_info/`);
  }

  searchSections(str: string) {
    const params = new HttpParams().set('section', str);
    return this.http.get<Section[]>(`${this.API_URL}/section/`, { params });
  }

  getSection(code: string) {
    return this.http.get<Section>(`${this.API_URL}/section/${code}/`);
  }

  getAdGroups() {
    return this.http.get<AdGroup[]>(`${this.API_URL}/adgroups/`);
  }

  getLnGroups() {
    return this.http.get<LnGroup[]>(`${this.API_URL}/lngroups/`);
  }

  searchRanks(str: string) {
    const params = new HttpParams().set('rank', str);
    return this.http.get<Rank[]>(`${this.API_URL}/rank/`, { params });
  }

  getRank(id: number) {
    return this.http.get<Rank>(`${this.API_URL}/rank/${id}/`);
  }

  getAdOuList() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/adou/`);
  }

  getLnAccTypes() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_acc_types/`);
  }

  getLnClientLicenses() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_client_licenses/`);
  }

  getLnMpsRanges() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mps_ranges/`);
  }

  getLnMailFileOwners() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mail_file_owners/`);
  }

  getLnMailSystems() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mail_systems/`);
  }

  getLnMailServers() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mail_servers/`);
  }

  getLnMailTemplates() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mail_templates/`);
  }

  getLnLicenseTypes() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_license_types/`);
  }

  getLnMailDomains() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/ln_mail_domains/`);
  }

  getDpRankCodes() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/dp_rank_codes/`);
  }

  getDpStaffCodes() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/dp_staff_codes/`);
  }

  getDpEmpTypes() {
    return this.http.get<SimpleCode[]>(`${this.API_URL}/dp_emp_types/`);
  }

  getRomaInfo(code: string) {
    return this.http.get<RomaInfo>(`${this.API_URL}/roma/${code}/`);
  }
}
