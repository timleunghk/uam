import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { BaseRequest } from '../models/models';

export interface NameChangeInfo {
  name: string[];
  force_change: boolean;
}
@Injectable()
export class CommunicationService {

  private objCompletedSource = new Subject<BaseRequest>();
  objCompleted$ = this.objCompletedSource.asObservable();
  completed(obj: BaseRequest) {
    this.objCompletedSource.next(obj);
  }

  private objHeaderSource = new Subject<string>();
  objHeader$ = this.objHeaderSource.asObservable();
  setHeader(obj: string) {
    this.objHeaderSource.next(obj);
  }

  private userNameSource = new Subject<NameChangeInfo>();
  userName$ = this.userNameSource.asObservable();
  setUserName(name: string[], force_change: boolean = true) {
    this.userNameSource.next({ name: name, force_change: force_change });
  }
}
